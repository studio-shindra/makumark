<template>
  <div>
    <h5 class="mb-3">お気に入り一覧</h5>

    <div
      v-for="item in items"
      :key="item.id"
      class="fav-row"
      @click="$emit('select', item.publish_date)"
    >
      <div>
        <div class="fav-date">{{ item.publish_date }}</div>
        <div class="fav-text">{{ item.original_text || item.text }}</div>
      </div>
      <div class="arrow">→</div>
    </div>

    <p v-if="items.length === 0" class="text-muted text-center py-3">
      お気に入りはありません
    </p>
  </div>
</template>

<script setup>
const props = defineProps({
  items: { type: Array, default: () => [] }
});
</script>

<style scoped>
.fav-row {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
}
.fav-date {
  font-size: 11px;
  color: #888;
}
.fav-text {
  font-size: 15px;
  color: #333;
}
.arrow {
  color: #666;
  font-size: 16px;
}
</style>