import { ref, computed } from 'vue';
import { Capacitor } from '@capacitor/core';

// グローバル User 状態管理
export const currentUser = ref(null);
export const authToken = ref(null);
export const isPremium = computed(() => currentUser.value?.is_premium || false);
export const isAuthenticated = computed(() => !!authToken.value);

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * アプリ起動時に認証状態を復元
 */
export async function restoreAuth() {
  const token = localStorage.getItem('auth_token');
  if (!token) return false;

  authToken.value = token;

  try {
    const user = await fetchMe();
    console.log('✅ 認証復元成功:', user);
    return true;
  } catch (error) {
    console.error('❌ 認証復元失敗:', error);
    logout();
    return false;
  }
}

/**
 * /api/me/ でユーザー情報を取得
 */
export async function fetchMe() {
  if (!authToken.value) {
    throw new Error('Not authenticated');
  }

  const res = await fetch(`${API_BASE}/api/me/`, {
    headers: {
      'Authorization': `Token ${authToken.value}`,
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch user: ${res.status}`);
  }

  const user = await res.json();
  currentUser.value = user;
  return user;
}

/**
 * Apple Sign-In
 */
export async function signInWithApple() {
  if (!Capacitor.isNativePlatform()) {
    console.warn('⚠️ Apple Sign-In は iOS でのみ動作します（デモモードで続行）');
    // デモモード: ローカルテスト用
    return signInDemo();
  }

  try {
    const { SignInWithApple } = await import('@capacitor-community/apple-sign-in');
    
    const result = await SignInWithApple.authorize({
      requestedScopes: [
        { scope: 0 }, // email
        { scope: 1 }, // fullName
      ],
    });

    const { user: appleUserId, identityToken, email } = result.response;

    // Backend に送信
    const res = await fetch(`${API_BASE}/api/auth/signin/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apple_id: appleUserId,
        id_token: identityToken,
        email: email || '',
      }),
    });

    if (!res.ok) {
      throw new Error(`Sign-in failed: ${res.status}`);
    }

    const data = await res.json();
    authToken.value = data.token;
    currentUser.value = data.user;
    
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('user_id', data.user.id);

    console.log('✅ Apple Sign-In 成功:', data.user);
    return data;

  } catch (error) {
    console.error('❌ Apple Sign-In エラー:', error);
    throw error;
  }
}

/**
 * デモモード: ローカルテスト用（Web ブラウザで動作確認）
 */
async function signInDemo() {
  const demoAppleId = `demo_user_${Date.now()}`;
  
  const res = await fetch(`${API_BASE}/api/auth/signin/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      apple_id: demoAppleId,
      email: 'demo@example.com',
    }),
  });

  if (!res.ok) {
    throw new Error(`Demo sign-in failed: ${res.status}`);
  }

  const data = await res.json();
  authToken.value = data.token;
  currentUser.value = data.user;
  
  localStorage.setItem('auth_token', data.token);
  localStorage.setItem('user_id', data.user.id);

  console.log('✅ デモモード サインイン成功:', data.user);
  return data;
}

/**
 * ログアウト
 */
export function logout() {
  authToken.value = null;
  currentUser.value = null;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_id');
  console.log('👋 ログアウト');
}

/**
 * 購読を検証（receipt を Backend に送信）
 */
export async function verifySubscription(receipt) {
  if (!authToken.value) {
    throw new Error('Not authenticated');
  }

  const res = await fetch(`${API_BASE}/api/subscription/verify/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${authToken.value}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ receipt }),
  });

  if (!res.ok) {
    throw new Error(`Subscription verify failed: ${res.status}`);
  }

  const user = await res.json();
  currentUser.value = user;
  console.log('✅ 購読検証成功:', user);
  return user;
}
