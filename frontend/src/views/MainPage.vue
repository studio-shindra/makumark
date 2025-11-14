<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import dayjs from "dayjs";
import { fetchTodayQuote, fetchQuoteByDate, toggleFavorite } from "@/api";
import { IconHeart, IconHeartFilled, IconBrandAmazon, IconShare2, IconMenuDeep } from "@tabler/icons-vue";
import html2canvas from "html2canvas";
import Sidebar from "@/components/Sidebar.vue";
import MainLayouts from "@/layouts/MainLayouts.vue";

const route = useRoute();

const quote = ref(null);
const loading = ref(true);
const error = ref("");

const isSidebarOpen = ref(false);

function openSidebar() {
  isSidebarOpen.value = true;
}



// 表示状態を計算
const displayState = computed(() => {
  if (loading.value) return "loading";
  if (error.value) return "error";
  return "content";
});

const today = dayjs();
const todayStr = today.format("YYYY-MM-DD");
const selectedDate = ref(todayStr);

// 画像シェア
const shareAreaVisible = ref(null);
const shareAreaHidden  = ref(null);
const sharing = ref(false);

async function onShareImage() {
  if (!shareAreaHidden.value || !quote.value) return;

  try {
    sharing.value = true;

    const canvas = await html2canvas(shareAreaHidden.value, {
      backgroundColor: "#ffffff",
      scale: 2,
      useCORS: true,
    });

    const dataUrl = canvas.toDataURL("image/png");
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
  <MainLayouts>
    <template #header>
      <!-- 日付ナビ -->
      <nav class="flex-fill df-center">
        <div class="d-flex gap-2 align-items-center justify-content-around day-buttons">
          <button
            v-for="d in navDays"
            :key="d.value"
            type="button"
            class="btn rounded-circle border-0"
            style="aspect-ratio: 1/1;"
            :class="[
              d.value === selectedDate
                ? 'btn-dark'
                : d.isToday
                ? 'btn-outline-dark'
                : 'btn-outline-secondary',
            ]"
            :disabled="d.isFuture"
            @click="onSelectDay(d)"
          >
            {{ d.label }}
          </button>
        </div>
        <!-- <small class="text-muted d-block mt-1">
          ※ 過去の日付をタップすると広告（いまは確認ダイアログ）が表示されます。
        </small> -->
      </nav>
    </template>

    <!-- 今日/選択日の台詞カード -->
    <section class="share d-flex h-100 position-relative">
      <div class="share-area flex-fill df-center" ref="shareAreaVisible">
        <div
          class="main-text-area d-grid h-100 w-100"
          :class="{
            'text-center text-muted py-5': displayState === 'loading',
            'text-center text-danger py-5': displayState === 'error',
          }"
        >
          <div class="main-text df-center flex-fill h-100  py-3 px-2">
            <p class="fs-4">
              {{ quote?.text }}
            </p>
          </div>
          <div class="author-area">
            <div class="author d-flex align-items-center justify-content-end flex-fill gap-3 me-4">
              <p class="mb-1 text-muted text-end d-flex align-items-end justify-content-center flex-column" v-if="quote && (quote.author_name || quote.source)">
                <template v-if="quote.author_name"><p class="mb-0">{{ quote.author_name }}</p></template>
                <template v-if="quote.source"><p class="mb-0">『{{ quote.source }}』</p></template>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <template #footer>
      <section class="footer-nav flex-fill d-flex justify-content-center align-items-start">
        <div class="share-button-area d-flex align-items-center justify-content-around">
          <div class="area d-flex align-itemns-center gap-3 justify-content-center bg-white py-1 px-5">
            <div class="d-flex align-items-center justify-content-center like-count small text-secondary">
              <!-- ハートボタン -->
              <button
                v-if="quote"
                @click="onToggleFavorite"
                class="btn p-0"
                style="background: rgba(255, 255, 255, 0.7); border-radius: 50%;"
              >
                <template v-if="quote.liked">
                  <IconHeartFilled
                    :size="26"
                    class="text-danger me-2"
                  />{{ quote.like_count }}
                </template>
                <template v-else>
                  <IconHeart
                    :size="26"
                    class="text-secondary me-2"
                  />{{ quote.like_count }}
                </template>
              </button>
            </div>
            <div class="amazon-link box d-flex align-items-center">
              <IconBrandAmazon />
            </div>
            <!-- 画像保存ボタン -->
            <div class="share-link">
              <button
                type="button"
                class="btn btn-outline-secondary border-0 p-0"
                :disabled="sharing || !quote"
                @click="onShareImage"
              >
                <IconShare2 />
              </button>
            </div>
            <div class="div">
              <button class="btn p-0" @click="openSidebar">
                <IconMenuDeep /><!-- ★このボタンで下のsidebarが開く -->
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- シェア専用（横書き） -->
      <div v-if="quote" class="share-area-hidden df-center flex-column" ref="shareAreaHidden">
        <p class="share-text">{{ quote.text }}</p>
        <div class="share-author">
          <template v-if="quote.author_name"><p>{{ quote.author_name }}</p></template>
          <template v-if="quote.source"><p>『{{ quote.source }}』</p></template>
        </div>
        <div class="share-icon df-center gap-2">
          <img src="/icon.png" style="width: 64px; height: 64px;" alt="">
          <div class="text">MakuMark</div>
        </div>
      </div>
    
    </template>
  </MainLayouts>

  <Sidebar v-model="isSidebarOpen" />
</template>



