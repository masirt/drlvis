import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";

import MainView from "../views/MainView.vue";
import Overview from "../views/Overview.vue";
import ConfidenceView from "../views/ConfidenceView.vue";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Home",
    component: Overview,
  },
  {
    path: "/confidence_view",
    name: "Confidence_View",
    component: ConfidenceView,
  },
  {
    path: "/overview",
    name: "Overview",
    component: Overview,
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
