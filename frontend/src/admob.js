import { Capacitor } from "@capacitor/core";
import {
  AdMob,
  BannerAdSize,
  BannerAdPosition,
} from "@capacitor-community/admob";

const bannerId = import.meta.env.VITE_ADMOB_BANNER_ID;
const interstitialId = import.meta.env.VITE_ADMOB_INTERSTITIAL_ID; // ← 追加

function canUseAdMob() {
  return Capacitor.isNativePlatform() && !!bannerId;
}
function canUseInterstitial() {
  return Capacitor.isNativePlatform() && !!interstitialId;
}

let initialized = false;

export async function initAdMob() {
  if (initialized) return;
  if (!Capacitor.isNativePlatform()) return;

  try {
    await AdMob.initialize();
    initialized = true;
  } catch (e) {
    console.warn("AdMob init failed", e);
  }
}

export async function showFooterBanner() {
  if (!canUseAdMob()) return;

  try {
    await initAdMob();
    await AdMob.showBanner({
      adId: bannerId,
      adSize: BannerAdSize.BANNER,
      position: BannerAdPosition.BOTTOM_CENTER,
    });
  } catch (e) {
    console.warn("AdMob banner failed", e);
  }
}

// ★ 過去の一行を見るとき用の全画面広告
export async function showPastQuoteInterstitial() {
  if (!canUseInterstitial()) return;

  try {
    await initAdMob();
    // インタースティシャル広告を準備して表示
    await AdMob.prepareInterstitial({
      adId: interstitialId,
    });
    await AdMob.showInterstitial();
  } catch (e) {
    console.warn("AdMob interstitial failed", e);
  }
}