import { createRouter, createWebHistory } from "vue-router";
import MainPage from "@/views/MainPage.vue";
import FavoritesPage from "@/views/FavoritesPage.vue";
import SettingsPage from "@/views/Settings.vue";

const routes = [
  { path: "/", name: "home", component: MainPage },
  { path: "/favorites", name: "favorites", component: FavoritesPage },
  { path: "/settings", name: "settings", component: SettingsPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;