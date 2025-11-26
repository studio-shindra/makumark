// src/versionCheck.js
import { Capacitor } from '@capacitor/core';
import { Browser } from '@capacitor/browser';

const CURRENT_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0';
const APP_STORE_URL = 'https://apps.apple.com/jp/app/makumark/id6739225748';
const LOOKUP_URL = 'https://itunes.apple.com/lookup?bundleId=com.studio-shindra.makumark&country=jp';

// 簡易セマンティックバージョン比較（"1.0.3" > "1.0.2" かどうか）
function isNewerVersion(remote, local) {
  const r = remote.split('.').map(n => parseInt(n || '0', 10));
  const l = local.split('.').map(n => parseInt(n || '0', 10));
  const len = Math.max(r.length, l.length);
  for (let i = 0; i < len; i++) {
    const rv = r[i] ?? 0;
    const lv = l[i] ?? 0;
    if (rv > lv) return true;
    if (rv < lv) return false;
  }
  return false;
}

export async function checkForUpdate() {
  try {
    // iTunes Search API から最新バージョンを取得
    const res = await fetch(LOOKUP_URL, { cache: 'no-cache' });
    if (!res.ok) {
      console.warn('version check: http error', res.status);
      return;
    }
    
    const data = await res.json();
    if (!data.results || data.results.length === 0) {
      console.warn('version check: no results from iTunes API');
      return;
    }

    const latestVersion = data.results[0].version;
    if (!latestVersion) {
      console.warn('version check: no version field in iTunes API response');
      return;
    }

    if (!CURRENT_VERSION) {
      console.warn('version check: CURRENT_VERSION not set');
      return;
    }

    if (!isNewerVersion(latestVersion, CURRENT_VERSION)) {
      // 自分の方が新しい or 同じ → 何もしない
      console.log(`version check: current ${CURRENT_VERSION} is up to date (latest: ${latestVersion})`);
      return;
    }

    // 新しいバージョンが利用可能
    const ok = window.confirm(
      `新しいバージョン ${latestVersion} が利用できます。\nApp Store を開きますか？`
    );
    if (!ok) return;

    if (Capacitor.isNativePlatform()) {
      await Browser.open({ url: APP_STORE_URL });
    } else {
      window.open(APP_STORE_URL, '_blank');
    }
  } catch (e) {
    console.error('version check failed', e);
  }
}
