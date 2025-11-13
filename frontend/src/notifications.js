import { Capacitor } from "@capacitor/core";
import { LocalNotifications } from "@capacitor/local-notifications";

const H_KEY = "makumark_notif_hour";
const M_KEY = "makumark_notif_minute";

const isNative = Capacitor.isNativePlatform();

function getSavedTime() {
  const h = Number(localStorage.getItem(H_KEY) ?? 9);
  const m = Number(localStorage.getItem(M_KEY) ?? 0);
  const hour = Math.min(23, Math.max(0, h || 0));
  const minute = Math.min(59, Math.max(0, m || 0));
  return { hour, minute };
}

/* ------------ 共通: 権限要求 ------------ */

async function requestBrowserPermission() {
  if (!("Notification" in window)) return false;
  if (Notification.permission === "granted") return true;
  const perm = await Notification.requestPermission();
  return perm === "granted";
}

async function requestNativePermission() {
  const perm = await LocalNotifications.checkPermissions();
  if (perm.display === "granted") return true;
  const req = await LocalNotifications.requestPermissions();
  return req.display === "granted";
}

/* ------------ 公開API: 毎日通知 ------------ */

export async function scheduleDailyNotification() {
  const { hour, minute } = getSavedTime();

  if (isNative) {
    // ★ iOS / Android（Capacitor）
    const ok = await requestNativePermission();
    if (!ok) {
      console.warn("Notification permission not granted (native)");
      return;
    }

    try {
      await LocalNotifications.cancel({ notifications: [{ id: 1 }] });
      await LocalNotifications.schedule({
        notifications: [
          {
            id: 1,
            title: "MakuMark",
            body: "幕間に一行、読みませんか？",
            schedule: {
              repeats: true,
              every: "day",
              on: { hour, minute },
            },
          },
        ],
      });
      console.log(
        `[native] scheduled daily at ${hour.toString().padStart(2, "0")}:${minute
          .toString()
          .padStart(2, "0")}`
      );
    } catch (e) {
      console.warn("scheduleDailyNotification native error", e);
    }
  } else {
    // ★ ブラウザ（開発用）: 本番ほど厳密ではないけど「動いてる感」を出す
    const ok = await requestBrowserPermission();
    if (!ok) {
      console.warn("Notification permission not granted (browser)");
      return;
    }

    // いったん「今から10秒後」に1回だけ通知を出す
    // （毎日分をブラウザで再現するのは現実的じゃないので簡易版）
    setTimeout(() => {
      new Notification("MakuMark", {
        body: `開発用テスト: 通知時刻 ${hour
          .toString()
          .padStart(2, "0")}:${minute.toString().padStart(2, "0")}`,
      });
    }, 1000);

    console.log("[web] scheduled dev notification (1回だけテスト)");
  }
}

/* ------------ 公開API: テスト通知 ------------ */

export async function showTestNotification() {
  if (isNative) {
    const ok = await requestNativePermission();
    if (!ok) {
      console.warn("Notification permission not granted (native)");
      return;
    }
    try {
      await LocalNotifications.schedule({
        notifications: [
          {
            id: 999,
            title: "MakuMark テスト",
            body: "これはテスト通知です（ネイティブ）。",
            schedule: { at: new Date(new Date().getTime() + 2000) }, // 2秒後
          },
        ],
      });
      console.log("[native] test notification scheduled");
    } catch (e) {
      console.warn("showTestNotification native error", e);
    }
  } else {
    // ブラウザ
    const ok = await requestBrowserPermission();
    if (!ok) {
      console.warn("Notification permission not granted (browser)");
      return;
    }
    new Notification("MakuMark テスト", {
      body: "これはテスト通知です（ブラウザ）。",
    });
    console.log("[web] test notification shown");
  }
}