<template>
  <div style="width: 100%">
    <confidence></confidence>
  </div>
</template>

<script lang="ts">
import Confidence from "./confidence-charts/Confidence.vue";
import { Component, Vue } from "vue-property-decorator";

@Component({
  components: { Confidence },
})
export default class ConfidenceView extends Vue {
  name: "ConfidenceView";
}
</script>
