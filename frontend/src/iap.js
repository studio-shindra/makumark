import { Capacitor } from "@capacitor/core";
import { registerPlugin } from "@capacitor/core";
import { IAP_PRODUCT_ID } from "@/constants";

// StoreKitプラグインを登録
const StoreKit = registerPlugin("StoreKit");

let initialized = false;

/**
 * StoreKit を初期化（実際にはStoreKit 2は自動初期化）
 */
export async function initPurchases() {
  if (initialized) return;
  if (!Capacitor.isNativePlatform()) {
    console.log('⚠️ IAP は Web では動作しません（デモモード）');
    return;
  }

  try {
    await StoreKit.initialize();
    initialized = true;
    console.log('✅ StoreKit 初期化成功');
  } catch (e) {
    console.error('❌ StoreKit 初期化失敗:', e);
  }
}

/**
 * プレミアムプランを購入
 */
export async function purchasePremium() {
  if (!Capacitor.isNativePlatform()) {
    // Web環境ではデモとして即座に成功
    console.log('🎭 デモモード: 購入成功');
    return {
      success: true,
      receipt: `demo_receipt_${Date.now()}`,
    };
  }

  try {
    await initPurchases();

    // 購入実行
    const result = await StoreKit.purchasePremium({
      productId: IAP_PRODUCT_ID,
    });

    console.log('✅ 購入成功:', result);

    return {
      success: true,
      transactionId: result.transactionId,
      productId: result.productId,
      receipt: result.transactionId, // トランザクションIDをレシートとして使用
    };
  } catch (e) {
    console.error('❌ 購入失敗:', e);
    
    // ユーザーがキャンセルした場合
    if (e.message?.includes('cancel')) {
      throw new Error('購入がキャンセルされました');
    }
    
    throw new Error('購入に失敗しました');
  }
}

/**
 * 購入を復元
 */
export async function restorePurchases() {
  if (!Capacitor.isNativePlatform()) {
    // Web環境ではデモとして即座に成功
    console.log('🎭 デモモード: 復元成功');
    return {
      success: true,
      isPremium: true,
    };
  }

  try {
    await initPurchases();

    const result = await StoreKit.restorePurchases();
    console.log('✅ 復元成功:', result);

    return {
      success: true,
      isPremium: result.isPremium,
    };
  } catch (e) {
    console.error('❌ 復元失敗:', e);
    throw new Error('復元に失敗しました');
  }
}

/**
 * 現在のプレミアム状態を確認
 */
export async function checkPremiumStatus() {
  if (!Capacitor.isNativePlatform()) {
    return false;
  }

  try {
    await initPurchases();

    const result = await StoreKit.checkPremiumStatus();
    console.log('📊 プレミアム状態:', result.isPremium);
    return result.isPremium;
  } catch (e) {
    console.error('❌ プレミアム状態確認失敗:', e);
    return false;
  }
}

// 以下は削除（StoreKitでは不要）
// export async function setUserID(userId) { ... }
// export async function clearUserID() { ... }

