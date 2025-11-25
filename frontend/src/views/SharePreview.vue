<template>
  <div class="container py-4 df-center" style="min-height: 80vh;">
    <!-- MainPage.vue と完全同一構造のシェア画像プレビュー -->
    <div class="share-canvas preview-visible" ref="shareAreaRef">
      <div class="share-area df-center flex-column p-3" style="background:#fff;">
        <div class="main-text df-center flex-fill h-100 py-3 px-2">
          <div class="fs-3 mb-0" style="white-space:pre-wrap;">
            この道を行けばどうなるものか 迷わず行けよ 行けばわかるさ
          </div>
          <div class="share-author mt-3">
            <p class="mb-0 name">太宰 治</p>
            <p class="mb-0 source">『人間失格』</p>
          </div>
        </div>
        <div class="d-flex align-items-center gap-2 mt-3">
          <img src="/logo-yoko.png" style="height:40px;" alt="icon" />
        </div>
      </div>
    </div>
    <div class="mt-4 text-center">
      <button class="btn btn-primary" @click="testCapture">画像として保存テスト</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import html2canvas from 'html2canvas';

const shareAreaRef = ref(null);

// html2canvas でキャプチャテスト
async function testCapture() {
  if (!shareAreaRef.value) return;
  
  try {
    const canvas = await html2canvas(shareAreaRef.value, {
      backgroundColor: "#ffffff",
      scale: 2,
      useCORS: true,
    });
    
    const dataUrl = canvas.toDataURL("image/png", 0.95);
    
    // ダウンロード
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `makumark_preview_${Date.now()}.png`;
    a.click();
    
    alert('画像を保存しました');
  } catch (e) {
    console.error('capture error', e);
    alert('キャプチャ失敗: ' + e.message);
  }
}
</script>

<style scoped>
/* custom.scss で left: -9999px になってる .share-canvas をプレビューでは表示 */
.share-canvas.preview-visible {
  position: static !important;
  left: auto !important;
  margin: 0 auto;
}
</style>

