<script setup>
import { IconX } from "@tabler/icons-vue";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);

function close() {
  emit("update:modelValue", false);
}
</script>

<template>
  <!-- 背景オーバーレイ -->
  <Transition name="fade">
    <div
      v-if="modelValue"
      class="modal-overlay position-fixed top-0 start-0 w-100 h-100"
      style="background: rgba(0, 0, 0, 0.5); z-index: 2000;"
      @click.self="close"
    ></div>
  </Transition>

  <!-- モーダル本体 -->
  <Transition name="slide-up">
    <div
      v-if="modelValue"
      class="modal-content position-fixed bg-white shadow-lg d-flex flex-column"
      style="
        bottom: 0;
        left: 0;
        right: 0;
        max-height: 80vh;
        border-radius: 20px 20px 0 0;
        z-index: 2001;
        padding: 1.5rem;
        padding-bottom: calc(1.5rem + env(safe-area-inset-bottom, 0px));
      "
    >
      <!-- ヘッダー -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="h5 mb-0">プライバシーポリシー</h3>
        <button class="btn btn-sm btn-outline-secondary border-0" type="button" @click="close">
          <IconX />
        </button>
      </div>

      <!-- コンテンツ -->
      <div class="flex-grow-1 overflow-auto">
        <div class="privacy-content">
          <p class="mb-3">
            MakuMark に掲載される文章は、翻訳文を転載したものではありません。
          </p>
          <p class="mb-3">
            すべての引用元は著作権の保護期間が満了した作品（パブリックドメイン）または、
            原文を元にAIが生成した「意訳・要約・説明文」です。
          </p>
          <p class="mb-0">
            本アプリは翻訳家が制作した翻訳文を使用しておらず、
            特定の翻訳者が創作した表現を引用または複製することもありません。
          </p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: transform 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.slide-up-leave-active {
  transition: transform 0.25s cubic-bezier(0.2, 0, 0, 1);
}

.slide-up-enter-from {
  transform: translateY(100%);
}

.slide-up-leave-to {
  transform: translateY(100%);
}

.privacy-content {
  line-height: 1.8;
  color: #333;
}

.privacy-content p {
  font-size: 0.95rem;
}
</style>
