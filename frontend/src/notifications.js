import { Capacitor } from "@capacitor/core";
import { LocalNotifications } from "@capacitor/local-notifications";
import { fetchTodayQuote } from "@/api";

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

/* ------------ 共通: 通知文言の組み立て ------------ */

async function buildNotificationContent() {
  try {
    const quote = await fetchTodayQuote();

    const author = quote.author_name || "劇作家の言葉";
    const source = quote.source || "";

    const title = "MakuMark";
    const body = source
      ? `${author}の言葉──『${source}』より引用`
      : `${author}の言葉`;

    return { title, body };
  } catch (e) {
    console.error("buildNotificationContent error", e);
    // 失敗したときのフォールバック
    return {
      title: "MakuMark",
      body: "劇作家の言葉",
    };
  }
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
  const { title, body } = await buildNotificationContent();

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
            title,
            body,
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
          .padStart(2, "0")} with body: ${body}`
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

    // いったん「今から1秒後」に1回だけ通知を出す
    setTimeout(() => {
      new Notification(title, {
        body: `${body}\n設定時刻: ${hour
          .toString()
          .padStart(2, "0")}:${minute.toString().padStart(2, "0")}`,
      });
    }, 1000);

    console.log("[web] scheduled dev notification (1回だけテスト)");
  }
}

/* ------------ 公開API: テスト通知 ------------ */

export async function showTestNotification() {
  const { title, body } = await buildNotificationContent();

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
            title,
            body,
            schedule: { at: new Date(new Date().getTime() + 2000) }, // 2秒後
          },
        ],
      });
      console.log("[native] test notification scheduled with body:", body);
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
    new Notification(title, { body });
    console.log("[web] test notification shown with body:", body);
  }
}

/* ------------ 公開API: 通知キャンセル ------------ */

export async function cancelDailyNotification() {
  if (isNative) {
    try {
      await LocalNotifications.cancel({ notifications: [{ id: 1 }] });
      console.log("[native] daily notification canceled");
    } catch (e) {
      console.warn("cancelDailyNotification error", e);
    }
  } else {
    console.log("[web] notification cancel (no-op in browser)");
  }
}