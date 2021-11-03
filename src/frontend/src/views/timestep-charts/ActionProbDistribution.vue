<template>
  <div id="action-distribution-chart" />
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { BarChart } from "../../util/BarChart";
import { StepActionMap } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEWIDTH } from "../Timestep.vue";

const general = namespace("General");
const timestep = namespace("Timestep");

@Component
export default class ActionProbDistribution extends Vue {
  name: "ActionProbDistribution";

  public barChart: BarChart;
  public barCreated = false;

  @general.State
  public currentAnimationFrame: number;

  @general.State
  public selectedEpisode: number;

  @timestep.State
  public frameData: any;

  @timestep.State
  public probData: StepActionMap;

  @timestep.Mutation
  public setProbData: (probData: StepActionMap) => void;

  @timestep.Mutation
  public setActionMeanings: (actionMeanings: string[]) => void;

  requestProbs(): void {
    (async () => {
      const probsResponse = await fetch(
        BASE_URL + `/get-probs?user=${this.selectedEpisode}`,
        {
          method: "GET",
        }
      );
      const probData = await probsResponse.json();
      this.setProbData(probData);
      if (this.barCreated) {
        this.updateBarChart(probData);
      } else {
        this.barCreated = true;
        this.createBarChart(probData);
      }
    })();
  }
  createBarChart(probData: StepActionMap): void {
    this.barChart = new BarChart(
      probData,
      "action-distribution-chart",
      [0, 1],
      "Action Probabilities",
      window.innerWidth * RELATIVEWIDTH,
      30
    );

    this.barChart.drawBarChart(this.currentAnimationFrame);
  }
  updateBarChart(probData: StepActionMap): void {
    this.barChart.updateData(probData);
    this.barChart.drawBarChart(this.currentAnimationFrame);
  }
  requestActionMeanings(): void {
    (async () => {
      const actionMeaningResponse = await fetch(
        BASE_URL + "/get-action-meanings",
        {
          method: "GET",
        }
      );

      const actionMeanings = await actionMeaningResponse.json();
      this.setActionMeanings(actionMeanings["action_meanings"]);
    })();
  }

  @Watch("currentAnimationFrame")
  public currentAnimationFrameChanged(newCurrentAnimationFrame: number): void {
    this.barChart.drawBarChart(newCurrentAnimationFrame);
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(): void {
    this.requestProbs();
  }

  mounted(): void {
    this.requestActionMeanings();
    this.requestProbs();
  }

  handleResize(e: any) {
    this.barChart.setWidth(window.innerWidth * RELATIVEWIDTH);
    this.barChart.drawBarChart(this.currentAnimationFrame);
  }

  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
