import { Capacitor } from "@capacitor/core";
import {
  AdMob,
  BannerAdSize,
  BannerAdPosition,
} from "@capacitor-community/admob";
import { isPremium } from "@/stores/user";

const bannerId = import.meta.env.VITE_ADMOB_BANNER_ID;
const rewardId = import.meta.env.VITE_ADMOB_REWARD_ID;

// 過去投稿解放フラグ（当日限り有効）
const PAST_UNLOCK_KEY = "makumark_past_unlocked";

function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function isPastUnlocked() {
  try {
    const val = localStorage.getItem(PAST_UNLOCK_KEY);
    return val === todayStr();
  } catch (e) {
    console.warn("[AdMob] read past unlock flag failed", e);
    return false;
  }
}

function setPastUnlocked() {
  try {
    localStorage.setItem(PAST_UNLOCK_KEY, todayStr());
  } catch (e) {
    console.warn("[AdMob] failed to set past unlock flag", e);
  }
}

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

function canUseReward() {
  console.log('[AdMob] reward check: isPremium =', isPremium.value);
  console.log('[AdMob] reward check: isNative =', Capacitor.isNativePlatform());
  console.log('[AdMob] reward check: rewardId =', rewardId);

  if (isPremium.value) {
    console.log('[AdMob] reward skip: premium user');
    return false;
  }
  if (isPastUnlocked()) {
    console.log('[AdMob] reward skip: already unlocked');
    return false;
  }
  if (!Capacitor.isNativePlatform()) {
    console.log('[AdMob] reward skip: not native platform');
    return false;
  }
  if (!rewardId) {
    console.log('[AdMob] reward skip: no rewardId');
    return false;
  }
  if (!rewardId.includes("/")) {
    console.warn("[AdMob] reward id looks invalid (expected ad unit id with '/'). Current value:", rewardId);
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

// 過去解放用のリワードゲート（名前は互換のためそのまま）
export async function showPastQuoteInterstitial() {
  console.log('[AdMob] showPastQuoteInterstitial() called (reward gate)');

  // プレミアム or 既に解放済みなら即OK
  if (isPremium.value || isPastUnlocked()) {
    console.log('[AdMob] past already unlocked or premium, skip ad');
    return true;
  }

  // リワードが使えない環境は無料解放にする
  if (!canUseReward()) {
    console.log('[AdMob] reward unavailable, unlock without ad');
    setPastUnlocked();
    return true;
  }

  try {
    await initAdMob();
    console.log('[AdMob] preparing reward video ad...');
    await AdMob.prepareRewardVideoAd({
      adId: rewardId,
    });
    console.log('[AdMob] showing reward video ad...');
    const rewardItem = await AdMob.showRewardVideoAd();
    console.log('[AdMob] reward received:', rewardItem);

    setPastUnlocked();
    return true;
  } catch (e) {
    console.error('[AdMob] reward ad failed or canceled:', e);
    return false;
  }
}

export function hasUnlockedPastQuotes() {
  return isPremium.value || isPastUnlocked();
}