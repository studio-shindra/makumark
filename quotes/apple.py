"""
Apple Sign-In id_token 検証 と App Store /verifyReceipt クライアント。

外部依存:
  - PyJWT[crypto]
  - requests
"""
from __future__ import annotations

import logging
import time
from typing import Any

import jwt
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"
APPLE_VERIFY_PROD = "https://buy.itunes.apple.com/verifyReceipt"
APPLE_VERIFY_SANDBOX = "https://sandbox.itunes.apple.com/verifyReceipt"

# JWKS の簡易キャッシュ（プロセス内、24h）
_JWKS_CACHE: dict[str, Any] = {"fetched_at": 0, "keys": []}
_JWKS_TTL = 60 * 60 * 24


class AppleVerificationError(Exception):
    """Apple 検証失敗。"""


def _fetch_apple_jwks() -> list[dict]:
    now = time.time()
    if _JWKS_CACHE["keys"] and (now - _JWKS_CACHE["fetched_at"]) < _JWKS_TTL:
        return _JWKS_CACHE["keys"]

    res = requests.get(APPLE_KEYS_URL, timeout=5)
    res.raise_for_status()
    keys = res.json().get("keys", [])
    _JWKS_CACHE["keys"] = keys
    _JWKS_CACHE["fetched_at"] = now
    return keys


def verify_apple_id_token(id_token: str, expected_sub: str | None = None) -> dict:
    """
    Apple Sign-In の id_token を検証して claims を返す。

    DEBUG=True かつ APPLE_VERIFY_SKIP_IN_DEBUG=1 のときは、
    署名検証をスキップして payload をそのまま返す（ローカル開発用）。
    """
    if not id_token:
        raise AppleVerificationError("id_token is empty")

    # 開発時のスキップ（本番では絶対通らない）
    if settings.DEBUG and getattr(settings, "APPLE_VERIFY_SKIP_IN_DEBUG", False):
        try:
            unverified = jwt.decode(id_token, options={"verify_signature": False})
            logger.warning("Apple id_token verification SKIPPED (DEBUG mode)")
            return unverified
        except Exception as e:
            raise AppleVerificationError(f"id_token decode failed: {e}")

    audience = getattr(settings, "APPLE_CLIENT_ID", "")
    if not audience:
        raise AppleVerificationError("APPLE_CLIENT_ID is not configured")

    try:
        unverified_header = jwt.get_unverified_header(id_token)
    except Exception as e:
        raise AppleVerificationError(f"invalid token header: {e}")

    kid = unverified_header.get("kid")
    if not kid:
        raise AppleVerificationError("missing kid in token header")

    keys = _fetch_apple_jwks()
    key = next((k for k in keys if k.get("kid") == kid), None)
    if key is None:
        # JWKS が更新されている可能性。キャッシュをクリアして再取得
        _JWKS_CACHE["keys"] = []
        keys = _fetch_apple_jwks()
        key = next((k for k in keys if k.get("kid") == kid), None)
    if key is None:
        raise AppleVerificationError(f"matching jwk not found for kid={kid}")

    try:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        decoded = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=audience,
            issuer=APPLE_ISSUER,
        )
    except jwt.PyJWTError as e:
        raise AppleVerificationError(f"jwt verification failed: {e}")

    if expected_sub and decoded.get("sub") != expected_sub:
        raise AppleVerificationError("sub mismatch with provided apple_id")

    return decoded


def verify_app_store_receipt(receipt_b64: str) -> dict:
    """
    /verifyReceipt エンドポイントに receipt を投げて検証結果を返す。
    本番に投げ、status==21007 ならサンドボックスに再送する。

    DEBUG時に APPLE_SHARED_SECRET 未設定なら検証をスキップして dummy 結果を返す。
    """
    if not receipt_b64:
        raise AppleVerificationError("receipt is empty")

    shared_secret = getattr(settings, "APPLE_SHARED_SECRET", "")

    if settings.DEBUG and getattr(settings, "APPLE_VERIFY_SKIP_IN_DEBUG", False) and not shared_secret:
        logger.warning("App Store receipt verification SKIPPED (DEBUG mode)")
        return {
            "status": 0,
            "_skipped": True,
            "latest_receipt_info": [],
        }

    if not shared_secret:
        raise AppleVerificationError("APPLE_SHARED_SECRET is not configured")

    payload = {
        "receipt-data": receipt_b64,
        "password": shared_secret,
        "exclude-old-transactions": True,
    }

    def _post(url: str) -> dict:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

    try:
        body = _post(APPLE_VERIFY_PROD)
    except requests.RequestException as e:
        raise AppleVerificationError(f"verifyReceipt request failed: {e}")

    # 21007 = "this receipt is from the sandbox environment, but it was sent to production"
    if body.get("status") == 21007:
        try:
            body = _post(APPLE_VERIFY_SANDBOX)
        except requests.RequestException as e:
            raise AppleVerificationError(f"sandbox verifyReceipt failed: {e}")

    if body.get("status") != 0:
        raise AppleVerificationError(f"verifyReceipt status={body.get('status')}")

    # bundle_id チェック
    expected_bundle = getattr(settings, "APPLE_CLIENT_ID", "")
    receipt_bundle = body.get("receipt", {}).get("bundle_id")
    if expected_bundle and receipt_bundle and receipt_bundle != expected_bundle:
        raise AppleVerificationError(
            f"bundle_id mismatch: receipt={receipt_bundle} expected={expected_bundle}"
        )

    return body


def extract_premium_expiry(verify_body: dict) -> int | None:
    """
    verifyReceipt のレスポンスから、有効な購読の expires_date_ms（最大値）を返す。
    自動更新されないIAP（買い切り）の場合は in_app から期限なしと見なして None を返す。
    """
    product_ids = set(getattr(settings, "APPLE_IAP_PRODUCT_IDS", []))
    latest = verify_body.get("latest_receipt_info") or verify_body.get("receipt", {}).get("in_app", [])
    if not latest:
        return None

    max_ms = 0
    for item in latest:
        if product_ids and item.get("product_id") not in product_ids:
            continue
        ms = item.get("expires_date_ms")
        if ms:
            try:
                max_ms = max(max_ms, int(ms))
            except (TypeError, ValueError):
                continue
    return max_ms or None
