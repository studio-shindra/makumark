import { createApp } from "vue";
import App from "@/App.vue";
import router from "@/router";

// Bootstrap (load SCSS so we can override variables)
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import '@/assets/styles/bootstrap-override.scss';
import '@/assets/styles/custom.scss';

const app = createApp(App);
app.use(router);
app.mount("#app");