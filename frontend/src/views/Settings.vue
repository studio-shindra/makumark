<script setup>
import { ref, onMounted } from "vue";
import { scheduleDailyNotification, showTestNotification } from "@/notifications";
import AccountSync from "@/components/AccountSync.vue";

const hour = ref(9);
const minute = ref(0);
const message = ref("");

// localStorage から読み込み
onMounted(() => {
  const h = localStorage.getItem("makumark_notif_hour");
  const m = localStorage.getItem("makumark_notif_minute");
  if (h !== null) hour.value = Number(h);
  if (m !== null) minute.value = Number(m);
});

function saveTime() {
  const h = Math.min(23, Math.max(0, Number(hour.value) || 0));
  const m = Math.min(59, Math.max(0, Number(minute.value) || 0));
  hour.value = h;
  minute.value = m;

  localStorage.setItem("makumark_notif_hour", String(h));
  localStorage.setItem("makumark_notif_minute", String(m));

  message.value = `通知時刻を ${h.toString().padStart(2, "0")}:${m
    .toString()
    .padStart(2, "0")} に保存しました。`;

  // ★ 通知を再スケジュール
  scheduleDailyNotification();
}

function handleSuccess(msg) {
  message.value = msg;
}

function handleError(msg) {
  message.value = msg;
}
</script>

<template>
  <div class="container py-4">
    <header class="mb-3">
      <h2 class="h5 mb-0">設定</h2>
      <small class="text-muted">MakuMark の動作をカスタマイズします。</small>
    </header>

    <section class="mb-4">
      <h3 class="h6">通知時刻</h3>
      <p class="small text-muted">
        「今日の一行」の通知を受け取りたい時間を設定します。（24時間表記）
      </p>

      <div class="d-flex align-items-center gap-2 mb-2">
        <input
          type="number"
          class="form-control"
          style="max-width: 80px;"
          v-model.number="hour"
          min="0"
          max="23"
        />
        <span>:</span>
        <input
          type="number"
          class="form-control"
          style="max-width: 80px;"
          v-model.number="minute"
          min="0"
          max="59"
        />
      </div>
      <div class="d-flex gap-2">
        <button type="button" class="btn btn-primary btn-sm" @click="saveTime">
          保存
        </button>
        <button
          type="button"
          class="btn btn-outline-secondary btn-sm"
          @click="showTestNotification"
        >
          テスト通知
        </button>
      </div>

      <p v-if="message" class="mt-2 small text-success">
        {{ message }}
      </p>
    </section>

    <!-- ver1: アカウント（コメントアウト） -->
    <!-- <AccountSync 
      class="mb-4"
      @success="handleSuccess"
      @error="handleError"
    /> -->

    <!-- メッセージ表示 -->
    <div v-if="message" class="alert" :class="message.includes('成功') || message.includes('保存') ? 'alert-success' : 'alert-danger'">
      {{ message }}
    </div>
  </div>
</template>