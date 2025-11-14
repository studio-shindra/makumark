<script setup>
import { useRouter } from "vue-router";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);

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
      style="width: 260px; padding: 1rem; z-index: 1051;"
    >
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 class="h6 mb-0">メニュー</h2>
        <button class="btn btn-sm btn-outline-secondary" type="button" @click="close">
          閉じる
        </button>
      </div>

      <nav class="d-flex flex-column gap-2">
        <button
          type="button"
          class="btn btn-light text-start"
          @click="goTo('settings')"
        >
          設定
        </button>
        <!-- 将来ここに他メニューを足せる -->
        <!-- <button type="button" class="btn btn-light text-start">お問い合わせ</button> -->
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