<template>
  <v-toolbar color="black" dense id="toolbar">
    <v-toolbar-title class="toolbar-text" style="min-width: 140px">
      <router-link
        :to="'/Overview'"
        custom
        style="text-decoration: none; color: white"
      >
        DRLVis
      </router-link>
    </v-toolbar-title>
    <!-- <span></span> -->
    <v-tabs background-color="black">
      <v-tabs-slider color="white" />
      <v-tab
        v-for="(item, index) in pages"
        :key="index"
        color="black"
        background-color="white"
      >
        <router-link class="list-item" :to="'/' + item" custom>
          {{ item.trim() }}
        </router-link>
      </v-tab>
    </v-tabs>
  </v-toolbar>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";

const general = namespace("General");
const confidence = namespace("Confidence");

@Component
export default class Header extends Vue {
  public pages = ["Overview", "Confidence_View"];

  @general.State
  public currentPage: string;

  @general.Mutation
  public setCurrentPage: (currentPage: string) => void;

  @confidence.Mutation
  public setCurrentEpisode: (episode: number) => void;

  public changePage(page: string) {
    this.setCurrentPage(page);
  }
}
</script>
<style scoped>
body {
  font-family: "Open Sans Regular";
}

#toolbar {
  color: white;
}
#menu {
  background-color: white;
  margin-top: 10%;
}
.button {
  border: 3px;
  border-color: white;
}
span {
  display: inline-block;
  width: 3%;
}

.list-item {
  text-decoration: none;
  color: white;
}
</style>
