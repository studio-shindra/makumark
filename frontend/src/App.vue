<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showFooterBanner, showPastQuoteInterstitial } from "@/admob";
import { LocalNotifications } from "@capacitor/local-notifications";
import { Capacitor } from "@capacitor/core";

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