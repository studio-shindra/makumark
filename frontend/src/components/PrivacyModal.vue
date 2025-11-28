<script setup>
// PrivacyModal is now a simple content component
// BaseModal wrapper is in MainLayouts.vue
</script>

<template>
  <div>
    <h5 class="mb-3">プライバシーポリシー</h5>

    <div class="privacy-content">
      <p class="mb-3">
        MakuMark に掲載される文章は、翻訳文を転載したものではありません。
      </p>
      <p class="mb-3">
        すべての引用元は著作権の保護期間が満了した作品（パブリックドメイン）または、
        原文を元にAIが生成した「意訳・要約・説明文」です。
      </p>
      <p class="mb-0">
        本アプリは翻訳家が制作した翻訳文を使用しておらず、
        特定の翻訳者が創作した表現を引用または複製することもありません。
      </p>
    </div>
  </div>
</template>

<style scoped>
.privacy-content {
  line-height: 1.8;
  color: #333;
}

.privacy-content p {
  font-size: 0.95rem;
}
</style>
