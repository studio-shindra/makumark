<script setup>
import { ref, computed, onMounted, watch, TransitionGroup, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useRoute } from "vue-router";
import dayjs from "dayjs";
import { fetchTodayQuote, fetchQuoteByDate, toggleFavorite, fetchWikipediaSummary } from "@/api";
import WikiModal from '@/components/WikiModal.vue';
import { Share } from '@capacitor/share';
import { IconHeart, IconHeartFilled, IconBrandAmazon, IconShare2, IconMenuDeep, IconBrandWikipedia, IconBadgeAdOff } from "@tabler/icons-vue";
import html2canvas from "html2canvas";
import MainLayouts from "@/layouts/MainLayouts.vue";
import { showPastQuoteInterstitial } from "@/admob";

const route = useRoute();
const router = useRouter();

const quote = ref(null);
const loading = ref(true);
const error = ref("");
const isTextVisible = ref(true); // テキストの表示/非表示を制御
const isAnimating = ref(false); // アニメーション中フラグ
const showSelectionIndicator = ref(true); // 選択日の丸表示を制御（ふわっと出す）

// MainLayoutsのrefを取得して、openSidebarを呼び出せるようにする
const mainLayoutsRef = ref(null);

function openSidebar() {
  mainLayoutsRef.value?.openSidebar();
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

// ナビ用ref
const navRef = ref(null);

// 画像シェア
const shareAreaVisible = ref(null);
const shareAreaHidden  = ref(null);
const sharing = ref(false);
// Wikipedia modal state
const wikiOpen = ref(false);
const wikiLoading = ref(false);
const wikiError = ref("");
const wikiSummary = ref(null);

// Amazon affiliate tag（.env に設定されていればそちらを優先）
const amazonTag = import.meta.env.VITE_AMAZON_TAG || 'shinblog0db-22';

// Amazon 検索 URL を生成（優先順: source（出典） -> author_name -> amazon_key）
const amazonSearchUrl = computed(() => {
  if (!quote.value) return null;
  const q = quote.value.source || quote.value.author_name || quote.value.amazon_key || '';
  if (!q) return 'https://amzn.to/4r0W82l'; // フォールバックの短縮リンク
  const encoded = encodeURIComponent(q);
  return `https://www.amazon.co.jp/s?k=${encoded}&tag=${amazonTag}`;
});

async function onShareImage() {
  if (!shareAreaHidden.value || !quote.value) return;

  try {
    sharing.value = true;

    const canvas = await html2canvas(shareAreaHidden.value, {
      backgroundColor: "#ffffff",
      scale: 2,
      useCORS: true,
    });

    // Canvas を blob に変換
    const blob = await new Promise((resolve) => {
      canvas.toBlob(resolve, "image/png", 0.95);
    });

    if (!blob) {
      alert("画像の生成に失敗しました。");
      return;
    }

    // Blob を File に変換
    const file = new File(
      [blob],
      `makumark_${dayjs().format("YYYYMMDD_HHmmss")}.png`,
      { type: "image/png" }
    );

    // Capacitor Share API で共有シートを表示
    await Share.share({
      title: "MakuMark",
      text: `台詞: ${quote.value.text?.slice(0, 50)}...`,
      files: [file.name], // ファイルパス
      dialogTitle: "シェア",
    });
  } catch (e) {
    console.error("share image error", e);
    if (e.message !== "Share canceled") {
      alert("シェアに失敗しました。");
    }
  } finally {
    sharing.value = false;
  }
}

// Wikipedia を開く（author を優先して検索）
async function onOpenWiki() {
  if (!quote.value) return;
  const query = quote.value.author_name || quote.value.text?.split('\n')?.[0]?.slice(0, 80) || '';
  if (!query) return;

  wikiLoading.value = true;
  wikiError.value = '';
  wikiSummary.value = null;

  try {
    const res = await fetchWikipediaSummary(query, 'ja');
    if (!res) {
      wikiError.value = '該当する記事が見つかりませんでした。';
    } else {
      wikiSummary.value = res;
      wikiOpen.value = true;
    }
  } catch (e) {
    console.error('wiki error', e);
    wikiError.value = 'Wikipedia の取得に失敗しました。';
  } finally {
    wikiLoading.value = false;
  }
}

// 初回：クエリに date があればそれを優先
onMounted(() => {
  const qDate = typeof route.query.date === "string" ? route.query.date : todayStr;
  selectedDate.value = qDate;
  loadQuoteFor(selectedDate.value);
  // 初期表示では選択インジケータを表示
  showSelectionIndicator.value = true;
});

// ルートのクエリパラメータ（date）が変わったら、selectedDateと表示を更新
const ignoreRouteWatch = ref(false);
watch(
  () => route.query.date,
  async (newDate, oldDate) => {
    // ignore フラグが立っている場合はこちらの更新による変更なので無視
    if (ignoreRouteWatch.value) {
      ignoreRouteWatch.value = false;
      return;
    }

    if (typeof newDate === "string" && newDate !== oldDate) {
      // animateパラメータがある場合はアニメーション付きで遷移
      if (route.query.animate === "true") {
        // 1. テキストをフェードアウト
        isTextVisible.value = false;
        
        // 2. カレンダーを更新（スライドアニメーションはCSSで）
        selectedDate.value = newDate;
        
        // 3. フェードアウトが終わってからデータをロード
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // 4. データをロード
        await loadQuoteFor(newDate);
        
        // 5. テキストをフェードイン
        await new Promise(resolve => setTimeout(resolve, 100));
        isTextVisible.value = true;
        
        // animateパラメータを削除
        router.replace({ name: "home", query: { date: newDate } });
      } else {
        // 通常の遷移（アニメーションなし）
        selectedDate.value = newDate;
        loadQuoteFor(newDate);
      }
    }
  }
);

// 7日分のナビ（日付と状態）
// 選択日を中央に表示するため、selectedDate を中心にレンジを作る
const navDays = computed(() => {
  const center = dayjs(selectedDate.value);
  const start = center.subtract(3, "day"); // 選択日の3日前から7日分
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

// （重複読み込みを防ぐため）二重の onMounted 呼び出しは削除しました。

// 日付ボタンクリック（アニメーション付きシーケンス）
async function onSelectDay(day) {
  if (day.isFuture) return; // 未来は押せない

  // 今日じゃなければ広告を挟む
  if (day.value !== todayStr) {
    const ok = window.confirm(
      "過去の台詞を見るには広告（いまはダミー）が表示されます。続けますか？"
    );
    if (!ok) return;

    // ネイティブ環境ならここでインタースティシャル表示
    await showPastQuoteInterstitial();
  }

  // アニメーションシーケンス開始
  try {
    isAnimating.value = true;

    // 少し間を置いて自然な感覚にする
    await new Promise((r) => setTimeout(r, 120));

    // 1) 本文と作者をフェードアウト
    isTextVisible.value = false;

    // フェードアウト完了を待つ（CSSの.leave-active 相当）
    await new Promise((r) => setTimeout(r, 420));

    // 2) ナビを横にスライドして選択日を中央へ（要素があるか確認）
    await nextTick();
    if (navRef.value) {
      const btn = navRef.value.querySelector(`[data-value="${day.value}"]`);
      if (btn && btn.scrollIntoView) {
        btn.scrollIntoView({ inline: "center", behavior: "smooth", block: "nearest" });
        // スライド完了を待つ
        await new Promise((r) => setTimeout(r, 600));
      }
    }

    // 3) 日付を選択表示（丸はまだ出さない）→少し遅延して丸をふわっと出す
    selectedDate.value = day.value;
    showSelectionIndicator.value = false;
    await new Promise((r) => setTimeout(r, 120));
    showSelectionIndicator.value = true; // ここで丸がふわっと出る
    await new Promise((r) => setTimeout(r, 380));

    // 4) データをロード
    await loadQuoteFor(day.value);

    // 少し待ってからフェードイン（本文）
    await new Promise((r) => setTimeout(r, 140));
    isTextVisible.value = true;
    await new Promise((r) => setTimeout(r, 450));

    // ルートを更新（履歴に残さない置換）
    // ただし watch による二重ロードを防ぐためフラグを立てる
    ignoreRouteWatch.value = true;
    router.replace({ name: "home", query: { date: day.value } });
  } finally {
    isAnimating.value = false;
  }
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
  <MainLayouts ref="mainLayoutsRef">
    <template #header>
      <!-- 日付ナビ -->
      <nav class="pt-5 flex-fill df-center" style="pointer-events: auto; position: relative; z-index: 10;">
        <div class="day-buttons" ref="navRef" style="pointer-events: auto; touch-action: manipulation;">
          <div class="d-flex gap-2 align-items-center justify-content-around w-100">
            <button
              v-for="d in navDays"
              :key="d.value"
              type="button"
              class="btn rounded-circle border-0"
              style="aspect-ratio: 1/1;"
              :data-value="d.value"
              :class="[
                d.value === selectedDate && showSelectionIndicator
                  ? 'btn-dark'
                  : d.isToday
                  ? 'btn-outline-dark'
                  : 'btn-outline-secondary',
              ]"
              :disabled="d.isFuture || isAnimating"
              @click="onSelectDay(d)"
            >
              {{ d.label }}
            </button>
          </div>
        </div>
        <!-- <small class="text-muted d-block mt-1">
          ※ 過去の日付をタップすると広告（いまは確認ダイアログ）が表示されます。
        </small> -->
      </nav>
    </template>
    <WikiModal v-model="wikiOpen" :summary="wikiSummary" :loading="wikiLoading" :error="wikiError" />

    <!-- 今日/選択日の台詞カード -->
    <section class="share d-flex h-100 position-relative">
      <div class="share-area flex-fill df-center" ref="shareAreaVisible">
        <div
          class="main-text-area w-100"
          :class="{
            'text-center text-muted py-5': displayState === 'loading',
            'text-center text-danger py-5': displayState === 'error',
          }"
        >
          <Transition name="fade-text">
            <div v-if="isTextVisible" class="main-text df-center flex-fill py-3 px-2">
              <p class="fs-4">
                {{ quote?.text }}
              </p>
            </div>
          </Transition>
          <div class="author-area">
            <Transition name="fade-text">
              <div v-if="isTextVisible" class="author d-flex align-items-center justify-content-end flex-fill gap-3 me-4">
                <div class="mb-1 text-muted text-end d-flex align-items-end justify-content-center flex-column" v-if="quote && (quote.author_name || quote.source)">
                  <template v-if="quote.author_name"><p class="mb-0">{{ quote.author_name }}</p></template>
                  <template v-if="quote.source"><p class="mb-0">『{{ quote.source }}』</p></template>
                </div>
              </div>
            </Transition>
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
              <a
                v-if="amazonSearchUrl"
                :href="amazonSearchUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="btn p-0"
              >
                <IconBrandAmazon />
              </a>
              <button
                v-else
                class="btn p-0"
                disabled
                style="opacity: 0.5; cursor: not-allowed;"
              >
                <IconBrandAmazon />
              </button>
            </div>
            <!-- wikipedia -->
            <div class="wiki">
              <button class="btn p-0" @click="onOpenWiki" :disabled="wikiLoading || !quote">
                <IconBrandWikipedia />
              </button>
            </div>
            <!-- 画像保存ボタン -->
            <div class="share-link">
              <button
                type="button"
                class="btn p-0"
                :disabled="sharing || !quote"
                @click="onShareImage"
              >
                <IconShare2 />
              </button>
            </div>
            <div class="upgrade">
              <button class="btn p-0" @click="mainLayoutsRef?.openUpgradeModal()">
                <IconBadgeAdOff />
              </button>
            </div>
            <div class="menu">
              <button class="btn p-0" @click="openSidebar">
                <IconMenuDeep />
              </button>
            </div>
          </div>
        </div>
      </section>


      <div v-if="quote">
        <div class="share-canvas"  ref="shareAreaHidden">
          <div class="share-area df-center flex-column p-3" style="background:#fff;">
              <div class="main-text df-center flex-fill h-100 py-3 px-2">
                <div class="fs-3 mb-0" style="white-space:pre-wrap;">
                  {{ quote.text }}
                </div>
          <div class="share-author mt-3">
          <p class="mb-0 name">{{ quote.author_name }}</p>
          <p class="mb-0 source">『{{ quote.source }}』</p>
          </div>
              </div>
            <div class="d-flex align-items-center gap-2 mt-3">
              <img src="/logo-yoko.svg" style="height:40px;" alt="icon" />
              <div class="text">MakuMark</div>
            </div>
          </div>
        </div>
      </div>


    </template>
  </MainLayouts>
</template>



