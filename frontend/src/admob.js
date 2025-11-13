import { Capacitor } from "@capacitor/core";
import {
  AdMob,
  BannerAdSize,
  BannerAdPosition,
} from "@capacitor-community/admob";

const bannerId = import.meta.env.VITE_ADMOB_BANNER_ID;

// まだネイティブじゃない（ブラウザ） or ID未設定なら何もしない用のガード
function canUseAdMob() {
  return Capacitor.isNativePlatform() && !!bannerId;
}

let initialized = false;

export async function initAdMob() {
  if (!canUseAdMob() || initialized) return;
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