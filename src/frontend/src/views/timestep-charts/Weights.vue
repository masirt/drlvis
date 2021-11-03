<template>
  <div>
    <div v-if="loaded">
      <div id="weight-histogram" />

      <v-radio-group row v-model="picked" class="radio-buttons" color="black">
        <v-radio
          color="black"
          key="count"
          label="Count"
          value="count"
        ></v-radio>
        <v-radio
          color="black"
          key="scaled"
          label="Scaled"
          value="scaled"
        ></v-radio>
      </v-radio-group>
    </div>
    <div class="progress-circle" v-else>
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { Histogram } from "../../util/Histogram";
import { WeightMatrix } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEWIDTH } from "../Timestep.vue";

const general = namespace("General");
const timestep = namespace("Timestep");

@Component
export default class Weights extends Vue {
  name: "Weights";

  public weightHistogram: Histogram;
  public histCreated = false;
  public picked = "count";
  public loaded = true;

  @general.State
  public selectedEpisode: number;

  @general.State
  public currentAnimationFrame: number;

  @timestep.Mutation
  public setScaleMinMax: (scaleMinMax: boolean) => void;

  @timestep.Mutation
  public setWeightMatrix: (weightMatrix: WeightMatrix) => void;

  requestWeightMatrix(): void {
    (async () => {
      const weightsResponse = await fetch(
        BASE_URL + `/get-weights-for-episode?user=${this.selectedEpisode}`,
        {
          method: "GET",
        }
      );

      const weightMatrix: WeightMatrix = await weightsResponse.json();
      this.setWeightMatrix(weightMatrix);
      if (this.histCreated) {
        this.weightHistogram.update(weightMatrix, 0);
      } else {
        this.weightHistogram = new Histogram(
          weightMatrix,
          "weight-histogram",
          "Weights",
          window.innerWidth * RELATIVEWIDTH
        );
        this.histCreated = true;
      }
    })();
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(): void {
    this.requestWeightMatrix();
  }

  @Watch("currentAnimationFrame")
  public currentAnimationFrameChanged(newCurrentAnimationFrame: number): void {
    if (this.weightHistogram) {
      this.weightHistogram.update({}, newCurrentAnimationFrame);
    }
  }

  @Watch("picked")
  public pickedChanged(newPicked: string): void {
    if (newPicked == "scaled") {
      this.setScaleMinMax(true);
    } else {
      this.setScaleMinMax(false);
    }
    this.weightHistogram.update({}, this.currentAnimationFrame);
  }

  mounted(): void {
    this.requestWeightMatrix();
  }

  handleResize(e: any) {
    this.weightHistogram.setWidth(window.innerWidth * RELATIVEWIDTH);
    this.weightHistogram.drawHistogram();
  }

  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
<style scoped>
.radio-buttons {
  margin-top: -3%;
  margin-left: 20%;
  color: #264653;
}

.progress-circle {
  margin: 0 auto;
  display: block;
}
</style>
