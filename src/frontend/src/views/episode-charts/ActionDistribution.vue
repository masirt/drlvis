<template>
  <div id="action-distributions-chart" />
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { BarChart } from "../../util/BarChart";
import { Action, StepActionMap } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEEPDISTWIDTH } from "../Episode.vue";

const general = namespace("General");
const timestep = namespace("Timestep");

@Component
export default class ActionDistribution extends Vue {
  name: "ActionDistribution";

  public barChart: BarChart;

  @general.State
  public selectedEpisode: number;

  @timestep.State
  public actionDistributionData: StepActionMap;

  @timestep.Mutation
  public setActionDistributionData: (actionDistribData: StepActionMap) => void;

  @timestep.Mutation
  public setActionMeanings: (actionMeanings: string[]) => void;

  createBarChart(actionDistribData: StepActionMap): void {
    const values: number[] = [];
    Object.values(actionDistribData).forEach((elem: Action, index) => {
      Object.values(elem).forEach((elem) => values.push(elem.value));
    });

    const maxBound = Math.max(...values);
    this.barChart = new BarChart(
      actionDistribData,
      "action-distributions-chart",
      [0, maxBound],
      "Action Distribution",
      window.innerWidth * RELATIVEEPDISTWIDTH,
      30
    );
    this.barChart.drawBarChart(this.selectedEpisode);
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

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(newSelectedEpisode: number): void {
    this.barChart.drawBarChart(newSelectedEpisode);
  }

  public requestActionDistributions(): void {
    (async () => {
      const actionDistResponse = await fetch(
        BASE_URL + `/get-action-distributions`,
        {
          method: "GET",
        }
      );
      const actionDistData = await actionDistResponse.json();
      this.setActionDistributionData(actionDistData);

      this.createBarChart(this.actionDistributionData);
    })();
  }

  beforeMount(): void {
    this.requestActionMeanings();
    this.requestActionDistributions();
  }

  handleResize(e: any) {
    this.barChart.setWidth(window.innerWidth * RELATIVEEPDISTWIDTH);
    this.barChart.drawBarChart(this.selectedEpisode);
  }
  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
