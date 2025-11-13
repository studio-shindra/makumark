<script setup>
import { IconHeart, IconTheater, IconMenuDeep } from "@tabler/icons-vue";

const props = defineProps({
  currentRouteName: { type: String, default: "" },
});

const emit = defineEmits(["go", "openSidebar"]);

function onGo(name) {
  emit("go", name);
}

function onOpenSidebar() {
  emit("openSidebar");
}
</script>

<template>
  <footer class="border-top bg-white">
    <div class="container py-2">
      <div class="d-flex justify-content-around">
        <button
          type="button"
          class="btn btn-link text-decoration-none"
          :class="currentRouteName === 'home' ? 'text-primary' : 'text-secondary'"
          @click="onGo('home')"
        >
          <IconTheater />
        </button>
        <button
          type="button"
          class="btn btn-link text-decoration-none"
          :class="currentRouteName === 'favorites' ? 'text-primary' : 'text-secondary'"
          @click="onGo('favorites')"
        >
          <IconHeart />
        </button>
        <button
          type="button"
          class="btn btn-link text-decoration-none text-secondary"
          @click="onOpenSidebar"
        >
          <IconMenuDeep />
        </button>
      </div>
    </div>
  </footer>
</template>