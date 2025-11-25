<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { scheduleDailyNotification, showTestNotification, cancelDailyNotification } from "@/notifications";
import AccountSync from "@/components/AccountSync.vue";

const hour = ref(9);
const minute = ref(0);
const message = ref("");
const isNotificationEnabled = ref(true); // 通知ON/OFF

// localStorage から読み込み（computedより先に実行）
const h = localStorage.getItem("makumark_notif_hour");
const m = localStorage.getItem("makumark_notif_minute");
const enabled = localStorage.getItem("makumark_notif_enabled");

if (h !== null) hour.value = Number(h);
if (m !== null) minute.value = Number(m);
if (enabled !== null) isNotificationEnabled.value = enabled === "true";

// time input用の HH:MM 形式の文字列
const timeString = computed({
  get: () => {
    return `${hour.value.toString().padStart(2, '0')}:${minute.value.toString().padStart(2, '0')}`;
  },
  set: (val) => {
    if (!val) return; // 空の場合は無視
    const [h, m] = val.split(":").map(Number);
    hour.value = h;
    minute.value = m;
  }
});

onMounted(() => {
  // 初期化完了後の処理があればここに
});

// 自動保存を削除（保存ボタンで明示的に保存）
// watch([hour, minute], () => {
//   if (isNotificationEnabled.value) {
//     saveTime();
//   }
// });

function saveTime() {
  const h = Math.min(23, Math.max(0, Number(hour.value) || 0));
  const m = Math.min(59, Math.max(0, Number(minute.value) || 0));
  hour.value = h;
  minute.value = m;

  localStorage.setItem("makumark_notif_hour", String(h));
  localStorage.setItem("makumark_notif_minute", String(m));

  const timeStr = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
  alert(`通知時刻を ${timeStr} に保存しました`);

  if (isNotificationEnabled.value) {
    scheduleDailyNotification();
  }
}

function toggleNotification() {
  isNotificationEnabled.value = !isNotificationEnabled.value;
  localStorage.setItem("makumark_notif_enabled", String(isNotificationEnabled.value));
  
  if (isNotificationEnabled.value) {
    alert("通知をONにしました");
    // ON時は再スケジュール
    scheduleDailyNotification();
  } else {
    alert("通知をOFFにしました");
    // OFF時は通知をキャンセル
    cancelDailyNotification();
  }
}

function handleSuccess(msg) {
  message.value = msg;
}

function handleError(msg) {
  message.value = msg;
}
</script>

<template>
  <div class="">
    <header class="mb-4">
      <h2 class="h5 mb-0">設定</h2>
      <small class="text-muted">MakuMark の動作をカスタマイズします。</small>
    </header>

    <!-- アラーム風の通知設定 -->
    <section class="notification-setting">
      <div class="">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h3 class="h6 mb-0">毎日の通知</h3>
            <small class="text-muted">今日のことばをお届けします</small>
          </div>
        </div>

        <!-- 時刻設定（ONの時のみ有効） -->
        <div class="time-picker bg-light d-flex w-100 p-2 align-items-center justify-content-between" :class="{ 'disabled': !isNotificationEnabled }">
          <div class="d-flex align-items-center justify-content-center gap-2 py-3 flex-fill">
            <input
              type="time"
              class="form-control form-control-lg text-center border-0"
              v-model="timeString"
              :disabled="!isNotificationEnabled"
              style="font-size: 1.5rem;"
            />
          </div>
          <!-- トグルスイッチ -->
          <div class="form-check form-switch">
            <input 
              class="form-check-input" 
              type="checkbox" 
              role="switch" 
              id="notificationToggle"
              v-model="isNotificationEnabled"
              @change="toggleNotification"
              style="width: 3rem; height: 1.5rem; cursor: pointer;"
            >
          </div>
        </div>
      </div>

      <button class="btn btn-dark text-white w-100 mt-3" @click="saveTime">保存</button>
    </section>

    <!-- ver1: アカウント（コメントアウト） -->
    <!-- <AccountSync 
      class="mb-4"
      @success="handleSuccess"
      @error="handleError"
    /> -->
  </div>
</template>

<style scoped>
.alarm-card {
  background: #f8f9fa;
}

.time-picker.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.form-control:disabled {
  background-color: #e9ecef;
  opacity: 0.6;
}

/* トグルスイッチのカスタマイズ */
.form-check-input:checked {
  background-color: orange;
  border-color: orange;
}
</style>