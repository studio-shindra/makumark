<template>
  <div v-if="modelValue" class="wiki-modal-backdrop" @click.self="close">
    <div class="wiki-modal content-card">
      <header class="d-flex justify-content-between align-items-center">
        <h3 class="mb-0">{{ summary?.title ?? 'Wikipedia' }}</h3>
        <button class="btn-close" @click="close">×</button>
      </header>

      <main class="mt-3" v-if="loading">
        <p class="text-muted">読み込み中...</p>
      </main>

      <main class="mt-3" v-else-if="error">
        <p class="text-danger">{{ error }}</p>
      </main>

      <main class="mt-3" v-else>
        <div v-if="summary">
          <p v-html="summary.extract_html || summary.extract"></p>
          <p class="text-muted small">出典: <a :href="summary.content_urls?.desktop?.page || summary.content_urls?.mobile?.page" target="_blank" rel="noopener">{{ summary.title }}</a></p>
        </div>
        <div v-else>
          <p class="text-muted">該当する記事が見つかりませんでした。</p>
        </div>
      </main>

      <footer class="mt-3 d-flex justify-content-end gap-2">
        <a v-if="summary" :href="summary.content_urls?.desktop?.page || summary.content_urls?.mobile?.page" class="btn btn-outline-secondary" target="_blank" rel="noopener">外部で開く</a>
        <button class="btn btn-primary" @click="close">閉じる</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: Boolean,
  summary: Object,
  loading: Boolean,
  error: String,
});
const emit = defineEmits(['update:modelValue']);

function close() {
  emit('update:modelValue', false);
}
</script>

<style scoped>
.wiki-modal-backdrop{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}
.wiki-modal{
  background: white;
  padding: 18px;
  width: min(720px, 96vw);
  max-height: 86vh;
  overflow: auto;
  border-radius: 12px;
}
.btn-close{
  background: transparent;
  border: 0;
  font-size: 20px;
}
</style>
