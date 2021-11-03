<template>
  <div class="main-container">
    <Episode class="episode" />
    <v-divider vertical style="margin: 1%"></v-divider>
    <Timestep class="timestep" />
  </div>
</template>

<script lang="ts">
import Episode from "./Episode.vue";
import Timestep from "./Timestep.vue";

import { Component, Vue } from "vue-property-decorator";

@Component({
  components: {
    Episode,
    Timestep,
  },
})
export default class Overview extends Vue {
  name: "Overview";
}
</script>

<style scoped>
.main-container {
  display: flex;
  flex-direction: row;
  /* overflow: auto; */
  height: 100%;
  width: 100%;
  overflow-x: scroll;
  overflow-y: hidden;
  font-family: "Open Sans Regular";
}

.episode {
  width: 50%;
}
</style>
