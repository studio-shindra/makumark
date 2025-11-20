<script setup>
import { ref, onMounted } from "vue";
import dayjs from "dayjs";
import { useRouter } from "vue-router";
import { fetchFavorites, toggleFavorite } from "@/api";
import { IconHeartFilled } from "@tabler/icons-vue";

const favorites = ref([]);
const loading = ref(true);
const error = ref("");

const router = useRouter();
const todayStr = dayjs().format("YYYY-MM-DD");

// 一覧取得
async function loadFavorites() {
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchFavorites();
    favorites.value = Array.isArray(data) ? data : [];
  } catch (e) {
    console.error(e);
    error.value = "いいねした台詞を読み込めませんでした。";
  } finally {
    loading.value = false;
  }
}

// 台詞カードクリック → メインページへ
async function onClickQuote(q) {
  if (!q.publish_date) {
    router.push({ name: "home" });
    return;
  }

  if (q.publish_date !== todayStr) {
    const ok = window.confirm(
      "過去の台詞を見るには広告動画が再生されます。続けますか？"
    );
    if (!ok) return;
  }

  router.push({
    name: "home",
    query: { date: q.publish_date },
  });
}

// ハートクリック → いいね解除でリストから消える
async function onToggleFavorite(q, event) {
  // カードクリックイベントを止める
  if (event) event.stopPropagation();

  try {
    const res = await toggleFavorite(q.id);
    if (!res.liked) {
      // いいね解除 → 一覧から削除
      favorites.value = favorites.value.filter((x) => x.id !== q.id);
    } else {
      // まだ liked のままならカウントだけ更新
      const target = favorites.value.find((x) => x.id === q.id);
      if (target) {
        target.like_count = res.like_count;
      }
    }
  } catch (e) {
    console.error("favorite toggle error", e);
  }
}

onMounted(() => {
  loadFavorites();
});
</script>

<template>
  <div class="container py-4">
    <header class="mb-3">
      <h2 class="h5 mb-0">いいねした台詞</h2>
      <small class="text-muted">ハートをつけた一行がここに並びます。</small>
    </header>

    <div v-if="loading" class="text-center text-muted py-5">
      読み込み中…
    </div>

    <div v-else-if="error" class="text-center text-danger py-5">
      {{ error }}
    </div>

    <div v-else>
      <div v-if="!favorites.length" class="text-muted py-4">
        まだいいねした台詞はありません。
      </div>

      <div class="d-flex flex-column gap-3">
        <div
          v-for="q in favorites"
          :key="q.id"
          class="card shadow-sm position-relative"
          role="button"
          @click="onClickQuote(q)"
        >
          <!-- ハート（解除ボタン） -->
          <button
            type="button"
            class="btn position-absolute top-0 end-0 m-2 p-1"
            style="background: rgba(255,255,255,0.7); border-radius: 50%;"
            @click="onToggleFavorite(q, $event)"
          >
            <IconHeartFilled :size="22" class="text-danger" />
          </button>

          <div class="card-body">
            <p class="fw-semibold mb-2">
              「{{ q.text }}」
            </p>
            <p class="mb-1 text-muted" v-if="q.author_name || q.source">
              <span v-if="q.author_name">{{ q.author_name }}</span>
              <span v-if="q.author_name && q.source"> / </span>
              <span v-if="q.source">{{ q.source }}</span>
            </p>
            <p class="mb-0 small text-secondary d-flex justify-content-between">
              <span>配信日: {{ q.publish_date }}</span>
              <span>❤️ {{ q.like_count }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>