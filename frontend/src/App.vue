<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Sidebar from "@/components/Sidebar.vue";
import FooterNav from "@/components/FooterNav.vue";
import { showFooterBanner } from "@/admob";

const route = useRoute();
const router = useRouter();

const isSidebarOpen = ref(false);

function go(name) {
  if (route.name !== name) {
    router.push({ name });
  }
}

function openSidebar() {
  isSidebarOpen.value = true;
}

onMounted(() => {
  // ブラウザでは何もしない。ネイティブのときだけバナー要求。
  showFooterBanner();
});
</script>

<template>
  <div class="bg-light min-vh-100 d-flex flex-column">
    <div class="flex-grow-1">
      <RouterView />
    </div>

    <!-- フッターメニュー（コンポーネント化） -->
    <FooterNav
      :current-route-name="route.name"
      @go="go"
      @openSidebar="openSidebar"
    />

    <!-- サイドバー -->
    <Sidebar v-model="isSidebarOpen" />
  </div>
</template>