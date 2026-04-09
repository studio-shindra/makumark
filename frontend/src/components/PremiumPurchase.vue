<script setup>
import { ref } from "vue";
import { isPremium, isAuthenticated, verifySubscription, signInWithApple, fetchMe } from "@/stores/user";
import { purchasePremium, restorePurchases } from "@/iap";

const emit = defineEmits(['success', 'error']);

const isProcessing = ref(false);

async function ensureSignedIn() {
  if (isAuthenticated.value) return true;
  try {
    await signInWithApple();
    return isAuthenticated.value;
  } catch (e) {
    console.error('sign-in required for purchase failed:', e);
    return false;
  }
}

async function handlePurchase() {
  if (isProcessing.value) return;
  isProcessing.value = true;

  try {
    // 課金前にサインイン必須（receipt をユーザーに紐付けるため）
    const ok = await ensureSignedIn();
    if (!ok) {
      emit('error', '❌ プレミアム購入にはサインインが必要です');
      return;
    }

    // IAP購入を実行
    const result = await purchasePremium();
    if (!result?.receipt) {
      emit('error', '❌ レシートを取得できませんでした');
      return;
    }

    // サーバ検証（必須）
    await verifySubscription(result.receipt);
    emit('success', '✅ プレミアム購読が有効になりました！');
  } catch (error) {
    console.error(error);
    if (error.message?.includes('キャンセル')) {
      emit('error', 'ℹ️ 購入がキャンセルされました');
    } else {
      emit('error', '❌ 購入処理に失敗しました');
    }
  } finally {
    isProcessing.value = false;
  }
}

async function handleRestore() {
  if (isProcessing.value) return;
  isProcessing.value = true;

  try {
    const ok = await ensureSignedIn();
    if (!ok) {
      emit('error', '❌ 復元にはサインインが必要です');
      return;
    }

    const result = await restorePurchases();
    if (result?.receipt) {
      await verifySubscription(result.receipt);
      emit('success', '✅ 購入を復元しました');
    } else if (result?.isPremium) {
      // receipt なしで復元成功した場合は念のためサーバ状態を取り直す
      await fetchMe();
      if (isPremium.value) {
        emit('success', '✅ 購入を復元しました');
      } else {
        emit('error', 'ℹ️ サーバ側にプレミアム情報が見つかりませんでした');
      }
    } else {
      emit('error', 'ℹ️ 復元可能な購入が見つかりませんでした');
    }
  } catch (error) {
    console.error(error);
    emit('error', '❌ 復元に失敗しました');
  } finally {
    isProcessing.value = false;
  }
}

// 親コンポーネントから呼び出せるように公開
defineExpose({
  handlePurchase,
  handleRestore,
});
</script>

<template>
  <section class="premium-purchase">
    <h2 class="h5 mb-2">プレミアムプラン</h2>
    <p class="small text-muted mb-3">
      この端末の MakuMark から広告が非表示になります。
    </p>

    <!-- すでにプレミアム -->
    <div v-if="isPremium" class="alert alert-success">
      <h6 class="mb-1">✅ プレミアム会員です</h6>
      <p class="small mb-0">
        広告が非表示になっています。
      </p>
    </div>

    <!-- まだプレミアムではない -->
    <div v-else>
      <div class="card mb-2">
        <div class="card-body d-flex justify-content-between align-items-end">
          <div>
            <p class="h4 mb-0">¥500</p>
            <small class="text-muted">/ 月</small>
          </div>
          <button
            type="button"
            class="btn btn-primary"
            @click="handlePurchase"
            :disabled="isProcessing"
          >
            {{ isProcessing ? '処理中...' : '広告を外す' }}
          </button>
        </div>
      </div>

      <button
        type="button"
        class="btn btn-link btn-sm p-0"
        @click="handleRestore"
        :disabled="isProcessing"
      >
        購入を復元
      </button>
    </div>
  </section>
</template>
