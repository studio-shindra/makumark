/**
 * アプリ全体で使用する定数
 */

// IAP Product ID
export const IAP_PRODUCT_ID = import.meta.env.VITE_IAP_PRODUCT_ID || 'com.studioshindra.makumark.premium';

// AdMob 広告ID
export const ADMOB_BANNER_ID = import.meta.env.VITE_ADMOB_BANNER_ID;
export const ADMOB_INTERSTITIAL_ID = import.meta.env.VITE_ADMOB_INTERSTITIAL_ID;

// API Base URL
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// Amazon Affiliate Tag
export const AMAZON_TAG = import.meta.env.VITE_AMAZON_TAG || 'shinblog0db-22';
