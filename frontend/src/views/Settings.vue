<script setup>
import { ref, onMounted } from "vue";
import { scheduleDailyNotification, showTestNotification } from "@/notifications";
import { currentUser, isPremium, isAuthenticated, signInWithApple, logout } from "@/stores/user";

const hour = ref(9);
const minute = ref(0);
const message = ref("");
const isProcessing = ref(false);

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

async function handleSignIn() {
  if (isProcessing.value) return;
  isProcessing.value = true;
  
  try {
    await signInWithApple();
    message.value = "サインインに成功しました";
  } catch (error) {
    console.error(error);
    message.value = "サインインに失敗しました";
  } finally {
    isProcessing.value = false;
  }
}

function handleLogout() {
  logout();
  message.value = "ログアウトしました";
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

    <!-- アカウント -->
    <section class="mb-4">
      <h3 class="h6">アカウント</h3>
      
      <div v-if="!isAuthenticated" class="mb-3">
        <p class="small text-muted">
          Apple でサインインすると、お気に入りや購読情報を複数デバイスで同期できます。
        </p>
        <button 
          type="button" 
          class="btn btn-dark btn-sm d-flex align-items-center gap-2"
          @click="handleSignIn"
          :disabled="isProcessing"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M11.182.008C11.148-.03 9.923.023 8.857 1.18c-1.066 1.156-.902 2.482-.878 2.516.024.034 1.52.087 2.475-1.258.955-1.345.762-2.391.728-2.43Zm3.314 11.733c-.048-.096-2.325-1.234-2.113-3.422.212-2.189 1.675-2.789 1.698-2.854.023-.065-.597-.79-1.254-1.157a3.692 3.692 0 0 0-1.563-.434c-.108-.003-.483-.095-1.254.116-.508.139-1.653.589-1.968.607-.316.018-1.256-.522-2.267-.665-.647-.125-1.333.131-1.824.328-.49.196-1.422.754-2.074 2.237-.652 1.482-.311 3.83-.067 4.56.244.729.625 1.924 1.273 2.796.576.984 1.34 1.667 1.659 1.899.319.232 1.219.386 1.843.067.502-.308 1.408-.485 1.766-.472.357.013 1.061.154 1.782.539.571.197 1.111.115 1.652-.105.541-.221 1.324-1.059 2.238-2.758.347-.79.505-1.217.473-1.282Z"/>
          </svg>
          Apple でサインイン
        </button>
      </div>
      <div v-else class="mb-3">
        <p class="small mb-2">
          <strong>{{ currentUser?.username || currentUser?.email || 'ユーザー' }}</strong>
          <span v-if="isPremium" class="badge bg-success ms-2">プレミアム</span>
        </p>
        <p class="small text-muted mb-2">
          サインインしています。お気に入りと購読情報が同期されます。
        </p>
        <button 
          type="button" 
          class="btn btn-outline-secondary btn-sm"
          @click="handleLogout"
        >
          ログアウト
        </button>
      </div>

    </section>
  </div>
</template>