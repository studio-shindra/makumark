// daily.js: 日付跨ぎ検知と日次最新化処理
import { fetchTodayQuote } from "@/api";
import { scheduleDailyNotification } from "@/notifications";

const LAST_QUOTE_DATE_KEY = "makumark_last_quote_date";
const NOTIF_ENABLED_KEY = "makumark_notif_enabled";

function isNotificationEnabled() {
  const v = localStorage.getItem(NOTIF_ENABLED_KEY);
  if (v === null) {
    // 既定は ON とする（Settings の初期値と合わせる）
    localStorage.setItem(NOTIF_ENABLED_KEY, "true");
    return true;
  }
  return v === "true";
}

function formatDateLocal(d) {
  return (
    d.getFullYear() +
    "-" +
    String(d.getMonth() + 1).padStart(2, "0") +
    "-" +
    String(d.getDate()).padStart(2, "0")
  );
}

// 日次状態を最新化する
// 1) 今日の引用を取得（常に）
// 2) 通知ONなら毎回スケジュールを上書き（過去に残った古いスケジュールを確実に置き換える）
// 3) 日付が変わっていたら日付スタンプ更新
// 戻り値: { quote, dayChanged }
export async function refreshDailyState() {
  const todayStr = formatDateLocal(new Date());
  const last = localStorage.getItem(LAST_QUOTE_DATE_KEY);
  const dayChanged = last !== todayStr;

  let quote = null;
  try {
    quote = await fetchTodayQuote();
  } catch (e) {
    console.error("refreshDailyState fetch error", e);
  }

  // 通知ONなら毎回再スケジュール（id=1 を cancel+set するので冪等）
  const notifEnabled = isNotificationEnabled();
  if (notifEnabled) {
    try {
      await scheduleDailyNotification();
    } catch (e) {
      console.warn("refreshDailyState notification reschedule error", e);
    }
  }

  if (dayChanged) {
    localStorage.setItem(LAST_QUOTE_DATE_KEY, todayStr);
  }

  return { quote, dayChanged };
}
