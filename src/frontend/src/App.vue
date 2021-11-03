<template>
  <v-app>
    <v-main>
      <Header class="header" />
      <div class="router-container">
        <router-view />
      </div>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from "vue";
import Header from "./views/Header.vue";

export default Vue.extend({
  name: "App",

  components: {
    Header,
  },

  data: () => ({}),
});
</script>

<style>
.v-application {
  height: 100%;
  width: 100;
}
.v-main {
  height: 100%;
  width: 100;
}
.v-main__wrap {
  display: flex;
  flex-direction: column;
  width: 100;
}
.header {
  flex-grow: 0;
  height: 10%;
  width: 100;
}
.router-container {
  display: flex;
  flex-grow: 1;
  height: 100%;
  width: 100;
}

@font-face {
  font-family: "Open Sans Regular";
  src: local("Open Sans Regular"),
    url(./util/fonts/Open_Sans/OpenSans-Regular.ttf) format("truetype");
}
</style>
