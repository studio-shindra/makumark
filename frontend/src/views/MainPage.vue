<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import dayjs from "dayjs";
import { fetchTodayQuote, fetchQuoteByDate, toggleFavorite } from "@/api";
import { IconHeart, IconHeartFilled } from "@tabler/icons-vue";
import html2canvas from "html2canvas";

const route = useRoute();

const quote = ref(null);
const loading = ref(true);
const error = ref("");

const today = dayjs();
const todayStr = today.format("YYYY-MM-DD");
const selectedDate = ref(todayStr);

// 画像シェア
const shareArea = ref(null);
const sharing = ref(false);

async function onShareImage() {
  if (!shareArea.value || !quote.value) return;

  try {
    sharing.value = true;

    // DOM要素取得
    const el = shareArea.value;

    // canvas生成
    const canvas = await html2canvas(el, {
      backgroundColor: "#ffffff", // 背景白で塗る
      scale: 2,                   // 解像度アップ（2倍）
      useCORS: true,              // 画像を後で使う場合の保険
    });

    // PNG データURL
    const dataUrl = canvas.toDataURL("image/png");

    // ダウンロード用リンクを作成
    const link = document.createElement("a");
    const todayStr = dayjs().format("YYYYMMDD");
    link.href = dataUrl;
    link.download = `makumark_${todayStr}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (e) {
    console.error("share image error", e);
    alert("画像の生成に失敗しました。");
  } finally {
    sharing.value = false;
  }
}

// 初回：クエリに date があればそれを優先
onMounted(() => {
  const qDate = typeof route.query.date === "string" ? route.query.date : todayStr;
  selectedDate.value = qDate;
  loadQuoteFor(selectedDate.value);
});

// 7日分のナビ（日付と状態）
const navDays = computed(() => {
  const start = today.subtract(3, "day"); // 今日の3日前から7日分
  const arr = [];
  for (let i = 0; i < 7; i++) {
    const d = start.add(i, "day");
    arr.push({
      label: d.date(), // 日にちだけ
      value: d.format("YYYY-MM-DD"),
      isToday: d.isSame(today, "day"),
      isFuture: d.isAfter(today, "day"),
    });
  }
  return arr;
});

// 共通ロード関数
async function loadQuoteFor(dateStr) {
  loading.value = true;
  error.value = "";
  try {
    let data;
    if (dateStr === todayStr) {
      data = await fetchTodayQuote();
    } else {
      data = await fetchQuoteByDate(dateStr);
    }
    quote.value = data;
  } catch (e) {
    console.error(e);
    if (e?.response?.status === 404) {
      error.value = "この日はまだ台詞が登録されていません。";
    } else {
      error.value = "台詞を読み込めませんでした。";
    }
  } finally {
    loading.value = false;
  }
}

// 初回：今日の台詞
onMounted(() => {
  loadQuoteFor(selectedDate.value);
});

// 日付ボタンクリック
async function onSelectDay(day) {
  if (day.isFuture) return; // 未来は押せない

  // 過去は広告ダミー
  if (day.value !== todayStr) {
    const ok = window.confirm(
      "過去の台詞を見るには広告動画（いまはダミー）が再生されます。続けますか？"
    );
    if (!ok) return;
  }

  selectedDate.value = day.value;
  await loadQuoteFor(day.value);
}

// いいねトグル
async function onToggleFavorite() {
  if (!quote.value) return;
  try {
    const res = await toggleFavorite(quote.value.id);
    quote.value.liked = res.liked;
    quote.value.like_count = res.like_count;
  } catch (e) {
    console.error("favorite error", e);
  }
}
</script>

<template>
  <div class="container py-4">
    <!-- ヘッダー -->
    <header class="mb-4 d-flex align-items-center gap-2">
      <div
        class="rounded-circle bg-dark text-white d-flex align-items-center justify-content-center"
        style="width: 36px; height: 36px;"
      >
        🐻
      </div>
      <div>
        <h1 class="h4 mb-0">MakuMark</h1>
        <small class="text-muted">幕間に読む、今日の一行。</small>
      </div>
    </header>

    <!-- 日付ナビ -->
    <nav class="mb-3">
      <div class="d-flex gap-2">
        <button
          v-for="d in navDays"
          :key="d.value"
          type="button"
          class="btn btn-sm"
          :class="[
            d.value === selectedDate
              ? 'btn-primary'
              : d.isToday
              ? 'btn-outline-primary'
              : 'btn-outline-secondary',
          ]"
          :disabled="d.isFuture"
          @click="onSelectDay(d)"
        >
          {{ d.label }}
        </button>
      </div>
      <small class="text-muted d-block mt-1">
        ※ 過去の日付をタップすると広告（いまは確認ダイアログ）が表示されます。
      </small>
    </nav>

    <!-- 今日/選択日の台詞カード -->
    <section>
      <div class="card shadow-sm position-relative">
        <!-- ハートボタン -->
        <button
          v-if="quote"
          @click="onToggleFavorite"
          class="btn position-absolute top-0 end-0 m-2 p-1"
          style="background: rgba(255, 255, 255, 0.7); border-radius: 50%;"
        >
          <IconHeartFilled
            v-if="quote.liked"
            :size="26"
            class="text-danger"
          />
          <IconHeart
            v-else
            :size="26"
            class="text-secondary"
          />
        </button>

        <div class="card-body share-area" ref="shareArea">
          <div v-if="loading" class="text-center text-muted py-5">
            読み込み中…
          </div>

          <div v-else-if="error" class="text-center text-danger py-5">
            {{ error }}
          </div>

          <div v-else>
            <p class="fs-4 fw-semibold mb-3" style="line-height: 1.6">
              「{{ quote.text }}」
            </p>

            <p class="mb-1 text-muted" v-if="quote.author">
              — {{ quote.author }}
            </p>

            <p class="small text-secondary">
              ❤️ {{ quote.like_count }}
            </p>

            <p class="mb-0 text-secondary small">
              配信日: {{ quote.publish_date }}
            </p>
          </div>
        </div>
      </div>
  <!-- 画像保存ボタン -->
  <div class="mt-3 text-end">
    <button
      type="button"
      class="btn btn-outline-secondary btn-sm"
      :disabled="sharing || !quote"
      @click="onShareImage"
    >
      {{ sharing ? "画像生成中…" : "画像を保存" }}
    </button>
  </div>
    </section>

    <footer class="footer-ad mt-3">
      <!-- ここにフッター広告入れる（いまはダミー） -->
    </footer>
  </div>
</template>