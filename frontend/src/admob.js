import { Capacitor } from "@capacitor/core";
import {
  AdMob,
  BannerAdSize,
  BannerAdPosition,
} from "@capacitor-community/admob";
import { isPremium } from "@/stores/user";

const bannerId = import.meta.env.VITE_ADMOB_BANNER_ID;
const interstitialId = import.meta.env.VITE_ADMOB_INTERSTITIAL_ID;

function canUseAdMob() {
  // プレミアムなら広告を表示しない
  if (isPremium.value) {
    console.log('✨ プレミアム会員: 広告をスキップ');
    return false;
  }
  return Capacitor.isNativePlatform() && !!bannerId;
}

function canUseInterstitial() {
  // プレミアムなら広告を表示しない
  if (isPremium.value) {
    console.log('✨ プレミアム会員: インタースティシャル広告をスキップ');
    return false;
  }
  
  if (!Capacitor.isNativePlatform()) return false;
  if (!interstitialId) return false;
  if (!interstitialId.includes("/")) {
    console.warn("AdMob interstitial id looks invalid (expected ad unit id with '/'). Current value:", interstitialId);
    return false;
  }
  return true;
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

export async function hideBanner() {
  if (!Capacitor.isNativePlatform()) return;
  
  try {
    await AdMob.hideBanner();
    console.log('✨ バナー広告を非表示にしました');
  } catch (e) {
    console.warn("AdMob hide banner failed", e);
  }
}

export async function showPastQuoteInterstitial() {
  if (!canUseInterstitial()) return;

  try {
    await initAdMob();
    await AdMob.prepareInterstitial({
      adId: interstitialId,
    });
    await AdMob.showInterstitial();
  } catch (e) {
    console.warn("AdMob interstitial failed", e);
  }
}