<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showFooterBanner, showPastQuoteInterstitial } from "@/admob";
import { initPurchases } from "@/iap";
import { LocalNotifications } from "@capacitor/local-notifications";
import { Capacitor } from "@capacitor/core";
import { restoreAuth } from "@/stores/user";

// 起動時の簡易ログ（安全な値のみ）
console.log('API_BASE =', import.meta.env.VITE_API_BASE);
console.log('mm_is_premium =', localStorage.getItem('mm_is_premium'));

const route = useRoute();
const router = useRouter();
const isSidebarOpen = ref(false);

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

onMounted(async () => {
  // 認証状態を復元（ここは await してOK）
  await restoreAuth();

  // IAP 初期化はアプリ描画を止めない（awaitしない・エラー握りつぶし）
  Promise.resolve()
    .then(() => initPurchases())
    .catch((e) => console.warn('IAP init skipped with error:', e));

  await ensureNotificationPermission();
  showFooterBanner(); // ネイティブのときだけ中で動くようにしてあるやつ
});
</script>


<template>
  <div class="h-100 d-flex flex-column">
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
</template>