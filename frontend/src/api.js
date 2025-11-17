import axios from "axios";

const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000";

const clientIdKey = "makumark_client_id";

export function getClientId() {
  let id = localStorage.getItem(clientIdKey);
  if (!id) {
    if (window.crypto && window.crypto.randomUUID) {
      id = window.crypto.randomUUID();
    } else {
      id = "mm-" + Math.random().toString(36).slice(2);
    }
    localStorage.setItem(clientIdKey, id);
  }
  return id;
}

// 認証 Token を取得
function getAuthToken() {
  return localStorage.getItem("auth_token");
}

// axios インスタンスに認証ヘッダーを動的に追加
const api = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 10000,
});

// リクエストインターセプター: Token があれば自動的に Authorization ヘッダーを追加
api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// 今日の1本を取得
export async function fetchTodayQuote() {
  const params = {};
  // Token がない場合のみ client_id を送る
  if (!getAuthToken()) {
    params.client_id = getClientId();
  }
  const res = await api.get("/quotes/today/", { params });
  return res.data;
}

// いいねトグル
export async function toggleFavorite(quoteId, isCampaign = false) {
  const data = { is_campaign: isCampaign };
  // Token がない場合のみ client_id を送る
  if (!getAuthToken()) {
    data.client_id = getClientId();
  }
  const res = await api.post(`/quotes/${quoteId}/toggle-favorite/`, data);
  return res.data; // { liked: true/false, like_count: N }
}

// 指定日付の台詞を取得
export async function fetchQuoteByDate(dateStr) {
  const params = { date: dateStr };
  // Token がない場合のみ client_id を送る
  if (!getAuthToken()) {
    params.client_id = getClientId();
  }
  const res = await api.get("/quotes/by-date/", { params });
  return res.data;
}

// いいね一覧を取得
export async function fetchFavorites() {
  const params = {};
  // Token がない場合のみ client_id を送る
  if (!getAuthToken()) {
    params.client_id = getClientId();
  }
  const res = await api.get("/quotes/favorites/", { params });
  return res.data; // [Quote...]
}

// Wikipedia 検索→サマリー取得
export async function fetchWikipediaSummary(query, lang = "ja") {
  if (!query) return null;
  // 1) 検索で候補を取得（MediaWiki API）
  const searchUrl = `https://${lang}.wikipedia.org/w/api.php`;
  const searchParams = {
    action: "query",
    list: "search",
    srsearch: query,
    format: "json",
    origin: "*",
    srlimit: 1,
  };

  const searchRes = await axios.get(searchUrl, { params: searchParams });
  const hits = searchRes.data?.query?.search;
  if (!hits || hits.length === 0) return null;

  const title = hits[0].title;

  // 2) REST summary を取得
  const summaryUrl = `https://${lang}.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;
  const summaryRes = await axios.get(summaryUrl);

  return summaryRes.data; // contains title, extract, extract_html, content_urls, etc.
}

// ========================================
// Tracking API
// ========================================

// Quote 表示を記録
export async function trackQuoteView(quoteId) {
  try {
    const clientId = await getClientId();
    await api.post("/tracking/quotes/view/", {
      quote_id: quoteId,
      client_id: clientId,
    });
  } catch (error) {
    console.error("trackQuoteView error:", error);
  }
}

// Quote クリック（Wiki/Amazon/Share）を記録
export async function trackQuoteClick(quoteId, action) {
  try {
    const clientId = await getClientId();
    await api.post("/tracking/quotes/click/", {
      quote_id: quoteId,
      client_id: clientId,
      action, // "wiki" | "amazon" | "share"
    });
  } catch (error) {
    console.error("trackQuoteClick error:", error);
  }
}

// Campaign 表示を記録
export async function trackCampaignView(campaignId) {
  try {
    const clientId = await getClientId();
    await api.post("/tracking/campaigns/view/", {
      campaign_id: campaignId,
      client_id: clientId,
    });
  } catch (error) {
    console.error("trackCampaignView error:", error);
  }
}

// Campaign クリック（公式サイト/SNS/Share）を記録
export async function trackCampaignClick(campaignId, action) {
  try {
    const clientId = await getClientId();
    await api.post("/tracking/campaigns/click/", {
      campaign_id: campaignId,
      client_id: clientId,
      action, // "official" | "sns" | "share"
    });
  } catch (error) {
    console.error("trackCampaignClick error:", error);
  }
}

// 統計サマリーを取得
export async function fetchStatsOverview(date = null) {
  const params = {};
  if (date) {
    params.date = date;
  }
  const res = await api.get("/tracking/stats/overview/", { params });
  return res.data;
}