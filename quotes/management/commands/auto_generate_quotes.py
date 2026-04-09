"""
月次自動生成コマンド。

デフォルトでは「来月分」の名台詞を生成する（その月に入る前に在庫を作る運用）。
generate_month_quotes に既存日スキップが入っているので冪等に再実行できる。

使い方:
    python manage.py auto_generate_quotes              # 来月分を生成
    python manage.py auto_generate_quotes --this-month # 今月分を生成
    python manage.py auto_generate_quotes --offset 2   # 2ヶ月先を生成

Heroku Scheduler 等で月次（例: 毎月25日 00:00 JST）に呼び出すことを想定。
"""
import datetime

from django.core.management import call_command
from django.core.management.base import BaseCommand


def _add_months(d: datetime.date, months: int) -> datetime.date:
    m_index = (d.month - 1) + months
    year = d.year + m_index // 12
    month = m_index % 12 + 1
    return datetime.date(year, month, 1)


class Command(BaseCommand):
    help = "翌月（または指定オフセット月）の名台詞を自動生成する。月次cron向け。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--this-month",
            action="store_true",
            help="今月分を生成する（デフォルトは来月）",
        )
        parser.add_argument(
            "--offset",
            type=int,
            default=None,
            help="今月から何ヶ月先を生成するか（--this-month より優先）",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="DBに保存せず、生成内容だけコンソールに表示する",
        )

    def handle(self, *args, **options):
        today = datetime.date.today()

        if options["offset"] is not None:
            offset = options["offset"]
        elif options["this_month"]:
            offset = 0
        else:
            offset = 1

        target = _add_months(today, offset)
        self.stdout.write(
            self.style.NOTICE(
                f"[auto_generate_quotes] today={today} target={target.year}-{target.month:02d} offset={offset}"
            )
        )

        call_command(
            "generate_month_quotes",
            target.year,
            target.month,
            dry_run=options["dry_run"],
        )
