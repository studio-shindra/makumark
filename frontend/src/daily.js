// daily.js: 日付跨ぎ検知と日次最新化処理
import { fetchTodayQuote } from "@/api";
import { scheduleDailyNotification } from "@/notifications";

const LAST_QUOTE_DATE_KEY = "makumark_last_quote_date";
const NOTIF_ENABLED_KEY = "makumark_notif_enabled";

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
// 2) 日付が変わっていたら通知を再スケジュール＆日付スタンプ更新
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

  if (dayChanged) {
    localStorage.setItem(LAST_QUOTE_DATE_KEY, todayStr);
    const notifEnabled = localStorage.getItem(NOTIF_ENABLED_KEY) === "true";
    if (notifEnabled) {
      try {
        await scheduleDailyNotification();
      } catch (e) {
        console.warn("refreshDailyState notification reschedule error", e);
      }
    }
  }

  return { quote, dayChanged };
}
