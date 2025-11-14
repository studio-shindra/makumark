import { createApp } from "vue";
import App from "@/App.vue";
import router from "@/router";

// Bootstrap
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

import '@/assets/styles/custom.scss';

const app = createApp(App);
app.use(router);
app.mount("#app");