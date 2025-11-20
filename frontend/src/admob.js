import { Capacitor } from "@capacitor/core";
import {
  AdMob,
  BannerAdSize,
  BannerAdPosition,
} from "@capacitor-community/admob";
import { isPremium } from "@/stores/user";

const bannerId = import.meta.env.VITE_ADMOB_BANNER_ID;
const interstitialId = import.meta.env.VITE_ADMOB_INTERSTITIAL_ID;

let bannerVisible = false;

function canUseAdMob() {
  console.log('[AdMob] check: isPremium =', isPremium.value);
  console.log('[AdMob] check: isNative =', Capacitor.isNativePlatform());
  console.log('[AdMob] check: bannerId =', bannerId);

  // プレミアムなら広告を表示しない
  if (isPremium.value) {
    console.log('[AdMob] skip: premium user');
    return false;
  }
  if (!Capacitor.isNativePlatform()) {
    console.log('[AdMob] skip: not native platform');
    return false;
  }
  if (!bannerId) {
    console.log('[AdMob] skip: no bannerId');
    return false;
  }
  return true;
}

function canUseInterstitial() {
  console.log('[AdMob] interstitial check: isPremium =', isPremium.value);
  console.log('[AdMob] interstitial check: isNative =', Capacitor.isNativePlatform());
  console.log('[AdMob] interstitial check: interstitialId =', interstitialId);

  // プレミアムなら広告を表示しない
  if (isPremium.value) {
    console.log('[AdMob] interstitial skip: premium user');
    return false;
  }
  
  if (!Capacitor.isNativePlatform()) {
    console.log('[AdMob] interstitial skip: not native platform');
    return false;
  }
  if (!interstitialId) {
    console.log('[AdMob] interstitial skip: no interstitialId');
    return false;
  }
  if (!interstitialId.includes("/")) {
    console.warn("[AdMob] interstitial id looks invalid (expected ad unit id with '/'). Current value:", interstitialId);
    return false;
  }
  return true;
}

let initialized = false;

export async function initAdMob() {
  if (initialized) {
    console.log('[AdMob] already initialized');
    return;
  }
  if (!Capacitor.isNativePlatform()) {
    console.log('[AdMob] skip init: not native');
    return;
  }

  try {
    console.log('[AdMob] initializing...');
    await AdMob.initialize({ requestTrackingAuthorization: true });
    initialized = true;
    console.log('[AdMob] initialized successfully');
  } catch (e) {
    console.error('[AdMob] init failed:', e);
  }
}

export async function showFooterBanner() {
  console.log('[AdMob] showFooterBanner() called');

  if (!canUseAdMob()) {
    console.log('[AdMob] canUseAdMob() returned false, skipping');
    return;
  }

  if (bannerVisible) {
    console.log('[AdMob] banner already visible, skip');
    return;
  }

  try {
    await initAdMob();
    console.log('[AdMob] requesting banner show...');
    await AdMob.showBanner({
      adId: bannerId,
      adSize: BannerAdSize.ADAPTIVE_BANNER,
      position: BannerAdPosition.BOTTOM_CENTER,
    });
    bannerVisible = true;
    console.log('[AdMob] banner show requested successfully');
  } catch (e) {
    console.error('[AdMob] banner failed:', e);
  }
}

export async function hideBanner() {
  console.log('[AdMob] hideBanner() called');

  if (!Capacitor.isNativePlatform()) {
    console.log('[AdMob] skip hide: not native');
    return;
  }
  
  try {
    await AdMob.hideBanner();
    bannerVisible = false;
    console.log('[AdMob] banner hidden successfully');
  } catch (e) {
    console.error('[AdMob] hide banner failed:', e);
  }
}

export async function showPastQuoteInterstitial() {
  console.log('[AdMob] showPastQuoteInterstitial() called');

  if (!canUseInterstitial()) {
    console.log('[AdMob] canUseInterstitial() returned false, skipping');
    return;
  }

  try {
    await initAdMob();
    console.log('[AdMob] preparing interstitial...');
    await AdMob.prepareInterstitial({
      adId: interstitialId,
    });
    console.log('[AdMob] showing interstitial...');
    await AdMob.showInterstitial();
    console.log('[AdMob] interstitial shown successfully');
  } catch (e) {
    console.error('[AdMob] interstitial failed:', e);
  }
}