<script setup>
import { useRouter } from "vue-router";
import { IconX, IconChevronRight } from "@tabler/icons-vue";
const props = defineProps({
  modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "openFavorites", "openSettings", "openUpgrade", "openPrivacy"]);

const router = useRouter();

function close() {
  emit("update:modelValue", false);
}

function goTo(name) {
  close();
  router.push({ name });
}
</script>

<template>
  <!-- 背景の黒いオーバーレイ -->
  <Transition name="fade">
    <div
      v-if="modelValue"
      class="position-fixed top-0 start-0 w-100 h-100"
      style="background: rgba(0, 0, 0, 0.4); z-index: 1050;"
      @click.self="close"
    ></div>
  </Transition>
  
  <!-- サイドバー本体（右側からスライドイン） -->
  <Transition name="slide-right">
    <div
      v-if="modelValue"
      class="position-fixed top-0 end-0 h-100 bg-white shadow d-flex flex-column"
      style="width: 80vw; padding: 1rem; padding-top: calc(1rem + env(safe-area-inset-top, 0px)); z-index: 1051;"
    >
      <div class="d-flex justify-content-end align-items-center mb-3">
        <button class="btn btn-sm btn-outline-secondary border-0" type="button" @click="close">
          <IconX />
        </button>
      </div>

      <nav class="d-flex flex-column justify-content-between gap-2 h-100">
        <div class="wrap d-flex flex-column gap-4">
          <!-- お気に入り -->
          <button
            type="button"
            class="btn btn-white text-start d-flex justify-content-between align-items-center py-2 px-0 border-bottom"
            @click="emit('openFavorites')"
            style="border-radius: 0;"
          >
            お気に入り<IconChevronRight />
          </button>

          <!-- 設定（モーダルで開く） -->
          <button
            type="button"
            class="btn btn-white text-start d-flex justify-content-between align-items-center py-2 px-0 border-bottom"
            @click="() => { close(); emit('openSettings'); }"
            style="border-radius: 0;" 
          >
            設定<IconChevronRight />
          </button>

          <button
            type="button"
            class="btn btn-white text-start d-flex justify-content-between align-items-center py-2 px-0 border-bottom"
            @click="() => { close(); emit('openPrivacy'); }"
            style="border-radius: 0;"
          >
          プライバシーポリシー<IconChevronRight />
          </button>

          <!-- ver1: 広告を外す（コメントアウト） -->
          <!-- <button
            type="button"
            class="btn btn-light text-start"
            @click="() => { close(); emit('openUpgrade'); }"
          >
            広告を外す
          </button> -->
        </div> <!-- //wrap -->
        <!-- やっぱり絶対入れたくない品位にかける -->
        <!-- <div class="ad">
          <div 
            class="wrap d-flex flex-column align-items-end"
            style="opacity: 0.3;">
            <div class="title small text-muted">WEB等デザイン制作なら</div>
            <a href="https://sk-tokyo.net/" target="_blank" class="logo"><img style="height: 30px;" src="/sk-logo-bk.png" alt=""></a>
          </div>
        </div> -->
        <div class="tome d-flex align-items-end w-100 justify-content-end" style="padding-bottom: calc(4rem + 16px + env(safe-area-inset-bottom, 0px)); position: relative; z-index: 1100;">
          <a href="https://studio-shindra.com/" target="_blank" class="logo"><img style="height: 24px;" src="/shindra-icon-bk.svg" alt=""></a>
        </div>
      </nav>
    </div>
  </Transition>
</template>

<style scoped>
/* フェードインアニメーション（背景） */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s cubic-bezier(0.2, 0, 0, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 右からスライドインアニメーション（サイドバー本体） */
.slide-right-enter-active {
  transition: transform 0.35s cubic-bezier(0.2, 0, 0, 1);
}

.slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.slide-right-enter-from {
  transform: translateX(100%);
}

.slide-right-leave-to {
  transform: translateX(100%);
}
</style>