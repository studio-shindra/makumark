<script setup>
import { ref } from "vue";
import { currentUser, isPremium, isAuthenticated, signInWithApple, verifySubscription } from "@/stores/user";

const message = ref("");
const isProcessing = ref(false);

async function handleSignIn() {
  if (isProcessing.value) return;
  isProcessing.value = true;
  
  try {
    await signInWithApple();
    message.value = "サインインに成功しました！";
  } catch (error) {
    console.error(error);
    message.value = "サインインに失敗しました";
  } finally {
    isProcessing.value = false;
  }
}

async function handlePurchasePremium() {
  if (isProcessing.value) return;
  isProcessing.value = true;
  
  try {
    // TODO: 実際の IAP 購入フロー
    // 今はデモとして receipt を送信
    const demoReceipt = `demo_receipt_${Date.now()}`;
    await verifySubscription(demoReceipt);
    message.value = "プレミアム購読が有効になりました！";
  } catch (error) {
    console.error(error);
    message.value = "購入処理に失敗しました";
  } finally {
    isProcessing.value = false;
  }
}
</script>

<template>
  <div class="container py-4">
    <header class="mb-3">
      <h2 class="h5 mb-0">プレミアムプラン</h2>
      <small class="text-muted">広告なしで MakuMark を楽しもう</small>
    </header>

    <!-- 未サインイン時 -->
    <section v-if="!isAuthenticated" class="mb-4">
      <div class="alert">
        <p class="mb-2">
          <strong>サインインが必要です</strong>
        </p>
        <p class="small mb-3">
          プレミアムプランを購入するには、まず Apple でサインインしてください。
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
    </section>

    <!-- サインイン済み -->
    <section v-else class="mb-4">
      <div class="card mb-3">
        <div class="card-body">
          <div class="d-flex align-items-center justify-content-between mb-2">
            <h5 class="card-title mb-0">{{ currentUser?.username || currentUser?.email || 'ユーザー' }}</h5>
            <span v-if="isPremium" class="badge bg-success">プレミアム</span>
          </div>
        </div>
      </div>

      <!-- すでにプレミアム -->
      <div v-if="isPremium" class="alert">
        <h6>プレミアム会員です</h6>
        <p class="small mb-0">
          広告が非表示になっています。複数デバイスでもプレミアム特典が適用されます。
        </p>
      </div>

      <!-- まだプレミアムではない -->
      <div v-else>
        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">プレミアムプラン</h5>
            <p class="card-text">
              広告を削除して、快適に名言を楽しめます。
            </p>
            <ul class="small">
              <li>バナー広告を非表示</li>
              <li>インタースティシャル広告を非表示</li>
              <li>複数デバイスで同期</li>
            </ul>
            <div class="d-flex align-items-end justify-content-between mt-3">
              <div>
                <p class="h4 mb-0">¥500</p>
                <small class="text-muted">/ 月</small>
              </div>
              <button 
                type="button" 
                class="btn btn-primary"
                @click="handlePurchasePremium"
                :disabled="isProcessing"
              >
                {{ isProcessing ? '処理中...' : '購入する' }}
              </button>
            </div>
          </div>
        </div>

        <p class="small text-muted">
          ※ 購入後、自動的に広告が非表示になります。<br>
          ※ デモ環境では即座に有効化されます。
        </p>
      </div>
    </section>

    <!-- メッセージ表示 -->
    <div v-if="message" class="alert" :class="message.startsWith('✅') ? 'alert-success' : 'alert-danger'">
      {{ message }}
    </div>
  </div>
</template>