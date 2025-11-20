<script setup>
import { ref } from "vue";
import PremiumPurchase from "@/components/PremiumPurchase.vue";
import AccountSync from "@/components/AccountSync.vue";

const message = ref("");

function handleSuccess(msg) {
  message.value = msg;
}

function handleError(msg) {
  message.value = msg;
}
</script>

<template>
  <div class="container py-4">
    <!-- ========== 1. 広告を外す（課金）========== -->
    <PremiumPurchase 
      class="mb-5"
      @success="handleSuccess"
      @error="handleError"
    />

    <!-- ========== 2. 端末情報を引き継ぐ（サインイン）========== -->
    <AccountSync 
      class="mb-4"
      @success="handleSuccess"
      @error="handleError"
    />

    <!-- メッセージ表示 -->
    <div v-if="message" class="alert" :class="message.startsWith('✅') ? 'alert-success' : 'alert-danger'">
      {{ message }}
    </div>
  </div>
</template>