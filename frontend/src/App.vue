<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showFooterBanner, showPastQuoteInterstitial } from "@/admob";
import { initPurchases } from "@/iap";
import { LocalNotifications } from "@capacitor/local-notifications";
import { Capacitor } from "@capacitor/core";
import { restoreAuth } from "@/stores/user";
import { refreshDailyState } from "@/daily";
import { App as CapacitorApp } from "@capacitor/app";
import gsap from 'gsap';

// 起動時の簡易ログ（安全な値のみ）
console.log('API_BASE =', import.meta.env.VITE_API_BASE);
console.log('mm_is_premium =', localStorage.getItem('mm_is_premium'));

const route = useRoute();
const router = useRouter();
const isSidebarOpen = ref(false);
const isReady = ref(false); // データ準備完了フラグ
const showLoader = ref(true); // ローダー表示制御（isReady後1秒で消す）

async function ensureNotificationPermission() {
  if (!Capacitor.isNativePlatform()) return;
  const perm = await LocalNotifications.checkPermissions();
  if (perm.display !== "granted") {
    await LocalNotifications.requestPermissions();
  }
}

function go(name) {
  if (route.name !== name) {
    router.push({ name });
  }
}

function openSidebar() {
  isSidebarOpen.value = true;
}

async function initApp() {
  try {
    // 日次最新化（引用取得 & 日付跨ぎなら通知再スケジュール）
    await refreshDailyState();
  } catch (e) {
    console.error('initial refresh error', e);
  } finally {
    isReady.value = true;
    setTimeout(() => {
      showLoader.value = false;
    }, 1000);
  }
}

function scheduleMidnightRefresh() {
  const now = new Date();
  const next = new Date(now);
  next.setHours(24, 0, 0, 0); // 次のローカル真夜中
  const ms = next.getTime() - now.getTime();
  setTimeout(async () => {
    try {
      await refreshDailyState();
    } catch (e) {
      console.warn('midnight refresh error', e);
    } finally {
      scheduleMidnightRefresh(); // 次の真夜中も再設定
    }
  }, ms);
}

onMounted(async () => {
  // アプリ初期ロード（ローディング制御）
  initApp();

  // フォアグラウンド復帰時に最新化
  CapacitorApp.addListener('resume', () => {
    refreshDailyState();
  });

  // 真夜中跨ぎ検知
  scheduleMidnightRefresh();

  // ローダーアイコンのGSAPアニメ（下→弾む→戻る）
  requestAnimationFrame(() => {
    const el = document.querySelector('.loader-icon');
    if (el) {
      gsap.fromTo(el,
        { y: 60, opacity: 0, scale: 0.95 },
        { duration: 2.0, y: 0, opacity: 1, scale: 1, ease: 'elastic.out(1,0.6)' }
      );
    }
  });

  // ver1: 認証状態を復元（コメントアウト）
  // await restoreAuth();

  // ver1: IAP 初期化（コメントアウト）
  // Promise.resolve()
  //   .then(() => initPurchases())
  //   .catch((e) => console.warn('IAP init skipped with error:', e));

  await ensureNotificationPermission();
  showFooterBanner(); // ネイティブのときだけ中で動くようにしてあるやつ
});
</script>


<template>
  <!-- フルスクリーンのローディングレイヤー -->
  <transition name="fade">
    <div
      v-if="showLoader"
      class="app-loader df-center"
    >
      <div class="text-center">
        <img src="/icon.svg" alt="MakuMark" class="loader-icon" style="height:40px;" />
      </div>
    </div>
  </transition>

  <!-- 本体 -->
  <transition name="fade">
    <div v-if="isReady" class="h-100 d-flex flex-column">
      <div class="flex-grow-1">
        <RouterView />
      </div>

      <!-- フッターメニュー（コンポーネント化） -->
      <!-- <FooterNav
        :current-route-name="route.name"
        @go="go"
        @openSidebar="openSidebar"
      /> -->

      <!-- サイドバー -->
      <!-- <Sidebar v-model="isSidebarOpen" /> -->
    </div>
  </transition>
</template>

<style>
.app-loader {
  position: fixed;
  inset: 0;
  background: #ffffff;
  z-index: 9999;
  pointer-events: none; /* 背面クリック防止（必要なら none を外す） */
}
.loader-icon { will-change: transform, opacity; }

/* ふわっと出る用の簡単トランジション */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>