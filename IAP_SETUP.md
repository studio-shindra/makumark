# MakuMark IAP（アプリ内課金）セットアップガイド

## 概要

MakuMarkアプリの課金機能は以下の構成で実装されています：

- **Product ID**: `com.studioshindra.makumark.premium`
- **課金プラットフォーム**: StoreKit 2（Apple公式）
- **対応プラットフォーム**: iOS 15+

## 1. App Store Connectでの設定

### Product IDの登録

1. [App Store Connect](https://appstoreconnect.apple.com) にアクセス
2. 「マイApp」→ MakuMark を選択
3. 左メニューから「サブスクリプション」を選択
4. 「+」ボタンで新規サブスクリプショングループを作成（まだない場合）
5. サブスクリプションを追加:
   - **製品ID**: `com.studioshindra.makumark.premium`
   - **サブスクリプション期間**: 1ヶ月（または希望の期間）
   - **価格**: ¥500（または希望の価格）
   - **ローカライズ情報**: 日本語で商品名と説明を入力

## 2. StoreKitConfiguration ファイル（オプション: Xcode テスト用）

Xcodeでローカルテストする場合、StoreKit Configuration ファイルを作成できます：

1. Xcode で `App.xcworkspace` を開く
2. File → New → File → StoreKit Configuration File
3. Product ID `com.studioshindra.makumark.premium` を追加
4. スキーム設定で StoreKit Configuration を選択

これにより、サンドボックスアカウントなしでローカルテストが可能になります。

## 3. 環境変数の設定

`.env.local` ファイルに以下を設定してください：

\`\`\`env
# AdMob 広告ID（本番用に変更）
VITE_ADMOB_BANNER_ID=ca-app-pub-XXXXXXXX/YYYYYYYYYY
VITE_ADMOB_INTERSTITIAL_ID=ca-app-pub-XXXXXXXX/ZZZZZZZZZZ

# IAP Product ID
VITE_IAP_PRODUCT_ID=com.studioshindra.makumark.premium

# API Base URL
VITE_API_BASE=https://your-backend-url.com

# Amazon Affiliate Tag
VITE_AMAZON_TAG=your-amazon-tag
\`\`\`

## 4. ビルドとデプロイ

### 開発環境でのテスト

\`\`\`bash
cd frontend
npm install
npm run build
npx cap sync ios
npx cap open ios
\`\`\`

Xcodeで実機（iOSデバイス）にインストールしてテスト。

### サンドボックステスト

1. App Store Connect で「テスター」を追加
2. iOSデバイスの「設定」→「App Store」→「サンドボックスアカウント」でログイン
3. アプリで課金をテスト（実際の請求はされません）

### 本番リリース

1. App Store Connect でサブスクリプションを「審査用に提出」
2. アプリのバイナリをアップロード
3. Appleの審査を通過後、本番環境で課金が有効化されます

## 5. コンポーネントの使用方法

### PremiumPurchase コンポーネント

課金UIを表示するコンポーネント：

\`\`\`vue
<template>
  <PremiumPurchase 
    @success="handleSuccess"
    @error="handleError"
  />
</template>

<script setup>
import PremiumPurchase from "@/components/PremiumPurchase.vue";

function handleSuccess(msg) {
  console.log('成功:', msg);
}

function handleError(msg) {
  console.error('エラー:', msg);
}
</script>
\`\`\`

### AccountSync コンポーネント

サインインUIを表示するコンポーネント：

\`\`\`vue
<template>
  <AccountSync 
    @success="handleSuccess"
    @error="handleError"
  />
</template>

<script setup>
import AccountSync from "@/components/AccountSync.vue";
</script>
\`\`\`

## 6. 動作フロー

### 課金（サインイン不要）

1. ユーザーが「広告を外す」ボタンをタップ
2. StoreKit 2 が Apple の課金ダイアログを表示
3. 購入成功 → `localStorage` にプレミアムフラグを保存
4. 広告が即座に非表示になる

### 購入の復元

1. ユーザーが「購入を復元」ボタンをタップ
2. StoreKit 2 が過去の購入を確認（`AppStore.sync()`）
3. 復元成功 → `localStorage` にプレミアムフラグを保存

### サインイン（任意）

1. ユーザーが「Apple でサインイン」をタップ
2. Apple Sign-In で認証
3. サーバにアカウント作成 or ログイン
4. お気に入りと課金情報が端末またぎで同期される

## 7. StoreKit 2 の利点

- **外部依存なし**: Apple公式APIのみ使用
- **シンプル**: async/await対応で実装が簡単
- **自動トランザクション監視**: バックグラウンドでも購入を検知
- **レシート不要**: トランザクション情報を直接取得

## 8. トラブルシューティング

### 課金が動作しない

- Product ID が App Store Connect で「承認済み」か確認
- サンドボックステスターでログインしているか確認
- Xcodeのログで StoreKit エラーを確認

### 広告が消えない

- `isPremium` の値を確認（DevTools Console）
- `localStorage` の `mm_is_premium` が `1` になっているか確認
- アプリを再起動してみる

### ビルドエラー

\`\`\`bash
npm install
npx cap sync ios
\`\`\`

を再実行してみてください。

## 9. 参考リンク

- [StoreKit 2 Documentation](https://developer.apple.com/documentation/storekit)
- [App Store Connect Help](https://help.apple.com/app-store-connect/)
- [Capacitor Plugin Development](https://capacitorjs.com/docs/plugins/creating-plugins)

---

**注意**: 本番環境では必ず `.env.local` ファイルを `.gitignore` に追加し、APIキーを公開リポジトリにコミットしないでください。
