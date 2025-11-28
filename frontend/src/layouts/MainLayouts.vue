<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import dayjs from "dayjs";
import BaseModal from "@/components/BaseModal.vue";
import FavoriteList from "@/components/FavoriteList.vue";
import Sidebar from "@/components/Sidebar.vue";
import PrivacyModal from "@/components/PrivacyModal.vue";
import { fetchFavorites } from "@/api";
import { showPastQuoteInterstitial } from "@/admob";
import Settings from '@/views/Settings.vue';
import Upgrade from '@/views/Upgrade.vue';

const isFavoriteOpen = ref(false);
const favorites = ref([]);
const router = useRouter();

const isSidebarOpen = ref(false);
const isSettingsOpen = ref(false);
const isPrivacyOpen = ref(false);
// ver1: Upgradeモーダル（コメントアウト）
// const isUpgradeOpen = ref(false);

const todayStr = dayjs().format("YYYY-MM-DD");

async function openFavorites() {
  // サイドバーを閉じる
  isSidebarOpen.value = false;
  
  // モーダルを開く前に、今日の日付にリセット（カレンダーと表示を今日にする）
  router.push({ name: "home", query: { date: todayStr } });
  
  // お気に入りデータを取得
  favorites.value = await fetchFavorites();
  
  // サイドバーのアニメーションが終わってからモーダルを開く(少し遅延)
  setTimeout(() => {
    isFavoriteOpen.value = true;
  }, 300); // サイドバーのアニメーション時間(0.3s)に合わせる
}

function openSettings() {
  // サイドバーを閉じる
  isSidebarOpen.value = false;

  // サイドバーのアニメーションが終わってからモーダルを開く
  setTimeout(() => {
    isSettingsOpen.value = true;
  }, 350);
}

function closeSettings() {
  isSettingsOpen.value = false;
  // 設定が閉じた後もサイドバーは閉じたままにする
}

function openPrivacy() {
  // サイドバーを閉じる
  isSidebarOpen.value = false;

  // サイドバーのアニメーションが終わってからモーダルを開く
  setTimeout(() => {
    isPrivacyOpen.value = true;
  }, 350);
}

// ver1: openUpgrade関数（コメントアウト）
// function openUpgrade() {
//   // サイドバーを閉じる
//   isSidebarOpen.value = false;

//   // サイドバーのアニメーションが終わってからモーダルを開く
//   setTimeout(() => {
//     isUpgradeOpen.value = true;
//   }, 350);
// }

async function jumpToDate(dateStr) {
  // 1. アラートを先に出す（過去の日付の場合）
  if (dateStr !== todayStr) {
    const ok = window.confirm(
      "過去の台詞を見るには広告が表示されます。続けますか？"
    );
    if (!ok) return;
    
    // ネイティブ環境ならここでインタースティシャル表示
    await showPastQuoteInterstitial();
  }
  
  // 2. モーダルを閉じる
  isFavoriteOpen.value = false;
  
  // 3. MainPageにアニメーション付きで遷移するよう通知
  // emitでMainPageに通知（少し遅延して、モーダルのアニメーションが始まってから）
  setTimeout(() => {
    // MainPageのjumpToDateWithAnimationを呼び出す
    // でも、MainPageは子コンポーネントなので、ref経由でアクセスする必要がある
    // 一旦、直接router.pushして、MainPageでwatchしてアニメーションを制御する
    router.push({ name: "home", query: { date: dateStr, animate: "true" } });
  }, 100);
}

function openSidebar() {
  isSidebarOpen.value = true;
}

// ver1: openUpgradeModal関数（コメントアウト）
// function openUpgradeModal() {
//   openUpgrade();
// }

// 親コンポーネントからopenSidebarを呼び出せるように公開
defineExpose({
  openSidebar,
  // ver1: openUpgradeModal（コメントアウト）
  // openUpgradeModal,
});
</script>

<template>
  <div class="main-page w-100 position-relative">
    <header class="header d-flex">
      <slot name="header"></slot>
    </header>

    <main class="position-relative">
      <slot></slot>
    </main>

    <footer class="footer d-flex">
      <slot name="footer"></slot>
    </footer>

    <!-- サイドバー（各ページ共通） -->
    <Sidebar
      v-model="isSidebarOpen"
      @openFavorites="openFavorites"
      @openSettings="openSettings"
      @openPrivacy="openPrivacy"
    />
    <!-- ver1: openUpgradeイベント（コメントアウト） -->
    <!-- @openUpgrade="openUpgrade" -->

    <!-- お気に入りモーダル -->
    <BaseModal v-model="isFavoriteOpen">
      <FavoriteList :items="favorites" @select="jumpToDate" />
    </BaseModal>

    <!-- 設定モーダル -->
    <BaseModal v-model="isSettingsOpen">
      <Settings v-model="isSettingsOpen" />
    </BaseModal>

    <!-- プライバシーポリシーモーダル -->
    <BaseModal v-model="isPrivacyOpen">
      <PrivacyModal />
    </BaseModal>

    <!-- ver1: プレミアムモーダル（コメントアウト） -->
    <!-- <BaseModal v-model="isUpgradeOpen">
      <Upgrade />
    </BaseModal> -->
  </div>
</template>