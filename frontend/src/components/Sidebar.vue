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
  <div
    v-if="modelValue"
    class="position-fixed top-0 start-0 w-100 h-100"
    style="background: rgba(0, 0, 0, 0.4); z-index: 1050;"
    @click.self="close"
  >
    <!-- サイドバー本体（右側からスライドイン） -->
    <div
      class="bg-white h-100 shadow d-flex flex-column"
      style="width: 260px; margin-left: auto; padding: 1rem;"
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
          ⚙ 設定
        </button>
        <!-- 将来ここに他メニューを足せる -->
        <!-- <button type="button" class="btn btn-light text-start">お問い合わせ</button> -->
      </nav>
    </div>
  </div>
</template>