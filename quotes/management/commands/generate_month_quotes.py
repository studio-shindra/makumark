#management/commands/generate_month_quotes.py

import calendar
import datetime
import json
import random
import time
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from openai import OpenAI

from quotes.models import Quote


# パブリックドメインの劇作家たち
PLAYWRIGHTS = [
    # 日本
    {"name_ja": "観阿弥", "name_original": "Kan'ami", "region": "JP"},
    {"name_ja": "世阿弥", "name_original": "Zeami", "region": "JP"},
    {"name_ja": "近松門左衛門", "name_original": "Chikamatsu Monzaemon", "region": "JP"},
    {"name_ja": "鶴屋南北", "name_original": "Tsuruya Namboku", "region": "JP"},
    {"name_ja": "河竹黙阿弥", "name_original": "Kawakita Mokuami", "region": "JP"},
    {"name_ja": "坪内逍遥", "name_original": "Tsubouchi Shoyo", "region": "JP"},
    {"name_ja": "島村抱月", "name_original": "Shimamura Hogetsu", "region": "JP"},
    {"name_ja": "岡本綺堂", "name_original": "Okamoto Kido", "region": "JP"},
    {"name_ja": "泉鏡花", "name_original": "Izumi Kyoka", "region": "JP"},

    # 英語圏
    {"name_ja": "ウィリアム・シェイクスピア", "name_original": "William Shakespeare", "region": "EN"},
    {"name_ja": "ベン・ジョンソン", "name_original": "Ben Jonson", "region": "EN"},
    {"name_ja": "オスカー・ワイルド", "name_original": "Oscar Wilde", "region": "EN"},
    {"name_ja": "ジョージ・バーナード・ショー", "name_original": "George Bernard Shaw", "region": "EN"},

    # フランス
    {"name_ja": "モリエール", "name_original": "Molière", "region": "FR"},
    {"name_ja": "ピエール・コルネイユ", "name_original": "Pierre Corneille", "region": "FR"},
    {"name_ja": "ジャン・ラシーヌ", "name_original": "Jean Racine", "region": "FR"},
    {"name_ja": "エドモン・ロスタン", "name_original": "Edmond Rostand", "region": "FR"},

    # ドイツ・北欧・ロシア
    {"name_ja": "ゲーテ", "name_original": "Johann Wolfgang von Goethe", "region": "DE"},
    {"name_ja": "フリードリヒ・シラー", "name_original": "Friedrich Schiller", "region": "DE"},
    {"name_ja": "ヘンリック・イプセン", "name_original": "Henrik Ibsen", "region": "NO"},
    {"name_ja": "アウグスト・ストリンドベリ", "name_original": "August Strindberg", "region": "SE"},
    {"name_ja": "アントン・チェーホフ", "name_original": "Anton Chekhov", "region": "RU"},
    {"name_ja": "ニコライ・ゴーゴリ", "name_original": "Nikolai Gogol", "region": "RU"},
]

MODEL_NAME = "gpt-4o-mini"  # gpt-5.1-miniが利用できない場合はこちらを使用


class Command(BaseCommand):
    help = "指定した年月の『今日の名台詞』を、パブリックドメインの劇作家から自動生成する。"

    def add_arguments(self, parser):
        parser.add_argument(
            "year",
            type=int,
            nargs="?",
            help="生成対象の年 (例: 2025)。省略時は今年。",
        )
        parser.add_argument(
            "month",
            type=int,
            nargs="?",
            help="生成対象の月 (1〜12)。省略時は今月。",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="DBに保存せず、生成内容だけコンソールに表示する",
        )

    def handle(self, *args, **options):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise CommandError("環境変数 OPENAI_API_KEY が設定されていません。")

        client = OpenAI(api_key=api_key)

        today = datetime.date.today()
        year = options["year"] or today.year
        month = options["month"] or today.month
        dry_run = options["dry_run"]

        if not (1 <= month <= 12):
            raise CommandError("month は 1〜12 で指定してください。")

        _, num_days = calendar.monthrange(year, month)

        self.stdout.write(
            self.style.NOTICE(
                f"=== {year}-{month:02d} の名台詞を自動生成します（{num_days}日分） dry_run={dry_run} ==="
            )
        )

        created_count = 0

        for day in range(1, num_days + 1):
            publish_date = datetime.date(year, month, day)

            # すでにその日のQuoteがあるならスキップ（dry-runモードではスキップ）
            if not dry_run:
                try:
                    if Quote.objects.filter(publish_date=publish_date).exists():
                        self.stdout.write(
                            self.style.WARNING(f"[SKIP] {publish_date} は既に登録済み")
                        )
                        continue
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"[DB接続エラー] {e} - dry-runモードで続行します")
                    )

            # 重複回避のため、何度か試行
            quote_obj = None
            for attempt in range(5):
                playwright = random.choice(PLAYWRIGHTS)
                try:
                    data = self._fetch_quote_from_openai(client, playwright)
                    # dry-runモードでは取得したJSONを表示
                    if dry_run:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"[JSON取得] {playwright['name_ja']}:\n{json.dumps(data, ensure_ascii=False, indent=2)}"
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[ERROR] {publish_date} {playwright['name_ja']} 取得失敗: {e}"
                        )
                    )
                    time.sleep(2)
                    continue

                text_ja = data.get("text_ja", "").strip()
                source_ja = data.get("source_ja", "").strip()
                text_original = data.get("text_original", "").strip()
                source_original = data.get("source_original", "").strip()
                wiki_url = data.get("wiki_url", "").strip()

                if not text_ja or not source_ja:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[RETRY] {publish_date} {playwright['name_ja']} 不完全なデータのため再試行"
                        )
                    )
                    continue

                # 既存と同じ日本語テキストなら再試行（dry-runモードではスキップ）
                if not dry_run:
                    try:
                        if Quote.objects.filter(text=text_ja).exists():
                            self.stdout.write(
                                self.style.WARNING(
                                    f"[RETRY] {publish_date} 重複テキスト検知 → 再生成"
                                )
                            )
                            continue
                    except Exception:
                        pass  # DB接続エラー時はスキップ

                # ここまで来たらOK
                quote_obj = {
                    "playwright": playwright,
                    "text_ja": text_ja,
                    "source_ja": source_ja,
                    "text_original": text_original,
                    "source_original": source_original,
                    "wiki_url": wiki_url,
                }
                break

            if not quote_obj:
                self.stdout.write(
                    self.style.ERROR(
                        f"[FAIL] {publish_date} 分の生成に5回失敗しました。手動で対応してください。"
                    )
                )
                continue

            pw = quote_obj["playwright"]
            msg = f"{publish_date} | {pw['name_ja']} / {quote_obj['source_ja']} | {quote_obj['text_ja'][:40]}..."

            if dry_run:
                self.stdout.write(self.style.NOTICE(f"[DRY-RUN] {msg}"))
            else:
                with transaction.atomic():
                    Quote.objects.create(
                        text=quote_obj["text_ja"],
                        original_text=quote_obj["text_original"],
                        author_name=pw["name_ja"],
                        source=quote_obj["source_ja"],
                        original_source=quote_obj["source_original"],
                        category="classic",
                        tags=f"戯曲,{pw['name_ja']}",
                        publish_date=publish_date,
                        is_public_domain=True,
                        amazon_key="青空文庫",
                        wiki_key=quote_obj["wiki_url"],
                        bg_image_url="",
                        like_count=0,
                    )
                self.stdout.write(self.style.SUCCESS(f"[OK] {msg}"))
                created_count += 1

            # API叩きすぎ防止のためちょっとだけ待つ
            time.sleep(1.2)

        self.stdout.write(
            self.style.SUCCESS(
                f"=== 完了: {year}-{month:02d} に {created_count} 件の名台詞を生成しました ==="
            )
        )

    def _fetch_quote_from_openai(self, client: OpenAI, playwright: dict) -> dict:
        """
        OpenAI から JSON 形式で 1件の名台詞データを取得する。
        戻り値の例:
        {
          "text_ja": "生きるべきか死ぬべきか、それが問題だ。",
          "text_original": "To be, or not to be, that is the question:",
          "source_ja": "ハムレット",
          "source_original": "Hamlet",
          "wiki_url": "https://ja.wikipedia.org/wiki/ハムレット"
        }
        """
        name_ja = playwright["name_ja"]
        name_en = playwright["name_original"]

        system_msg = (
            "あなたは戯曲と古典劇に詳しい文学研究者です。"
            "パブリックドメインになっている古典劇から、印象的な名台詞を1つだけ選んでください。"
            "絶対に著作権の残っている作家や作品は使わないでください。"
        )

        user_msg = f"""
次の劇作家の戯曲から、印象的な台詞を1つだけ選んでください。

- 劇作家名（日本語）：{name_ja}
- 劇作家名（原綴）：{name_en}

制約:
- 著作権がすでに消滅している作品のみを対象としてください。
- 台詞は「1〜2文」くらいの長さにしてください。
- 日本語訳と、可能であれば原文も出してください。
- 出典となる作品名（日本語タイトルと原題）を出してください。
- 可能であればその作品の「日本語版WikipediaページのURL」を出してください。分からなければ空文字で構いません。

必ず次の形式の JSON オブジェクトだけを返してください（説明文は一切不要）:

{{
  "text_ja": "日本語の台詞",
  "text_original": "原文の台詞（分からなければ空文字）",
  "source_ja": "作品名の日本語タイトル",
  "source_original": "作品名の原題",
  "wiki_url": "日本語版WikipediaのURL（分からなければ空文字）"
}}
        """.strip()

        resp = client.chat.completions.create(
            model=MODEL_NAME,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )

        content = resp.choices[0].message.content
        data = json.loads(content)
        return {
            "text_ja": data.get("text_ja", ""),
            "text_original": data.get("text_original", ""),
            "source_ja": data.get("source_ja", ""),
            "source_original": data.get("source_original", ""),
            "wiki_url": data.get("wiki_url", ""),
        }