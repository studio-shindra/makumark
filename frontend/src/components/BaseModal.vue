<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click.self="close">
        <div class="modal-card">
          <!-- 好きな中身を slot で差し込む -->
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean
});
const emit = defineEmits(["update:modelValue"]);

function close() {
  emit("update:modelValue", false);
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.55);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.modal-card {
  width: 90%;
  max-width: 480px;
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 4px 18px rgba(0,0,0,0.25);
}

/* モーダルオーバーレイのフェードインアニメーション */
.modal-enter-active {
  transition: opacity 0.3s cubic-bezier(0.2, 0, 0, 1);
}

.modal-enter-active .modal-card {
  transition: opacity 0.4s cubic-bezier(0.2, 0, 0, 1) 0.3s,
              transform 1s cubic-bezier(0.2, 0, 0, 1) 0.3s;
}

.modal-leave-active {
  transition: opacity 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.modal-leave-active .modal-card {
  transition: opacity 0.2s cubic-bezier(0.2, 0, 0, 1),
              transform 0.2s cubic-bezier(0.2, 0, 0, 1);
}

.modal-enter-from {
  opacity: 0;
}

.modal-enter-from .modal-card {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.modal-leave-to {
  opacity: 0;
}

.modal-leave-to .modal-card {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}
</style>