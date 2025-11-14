<template>
  <div class="main-page d-grid min-vh-100 w-100 position-relative">
    <header class="header d-flex">
      <slot name="header"></slot>
    </header>

    <main class="position-relative">
      <slot></slot>
    </main>

    <footer class="footer d-flex">
      <slot name="footer"></slot>
    </footer>
  </div>
</template>
