<template>
  <div id="reward-chart" />
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { StepValueMap } from "../../util/types";
import { DynamicBarChart } from "../../util/DynamicBarChart";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEWIDTH } from "../Timestep.vue";

const general = namespace("General");
const timestep = namespace("Timestep");

@Component
export default class Reward extends Vue {
  name: "Reward";

  public dynamicBarChart: DynamicBarChart;
  public dynamicBarChartCreated = false;

  @general.State
  public currentAnimationFrame: number;

  @general.State
  public selectedEpisode: number;

  @timestep.State
  public rewardData: StepValueMap;

  @timestep.Mutation
  public setRewardData: (rewardData: StepValueMap) => void;

  requestRewards(): void {
    (async () => {
      const rewardResponse = await fetch(
        BASE_URL + `/get-rewards?user=${this.selectedEpisode}`,
        {
          method: "GET",
        }
      );
      const rewardData = await rewardResponse.json();
      this.setRewardData(rewardData);
      if (this.dynamicBarChartCreated) {
        this.updateDynamicScatterplot(rewardData);
      } else {
        this.dynamicBarChartCreated = true;
        this.createDynamicScatterplot(rewardData);
      }
    })();
  }
  createDynamicScatterplot(rewardData: StepValueMap): void {
    this.dynamicBarChart = new DynamicBarChart(
      rewardData,
      "reward-chart",
      "Reward",
      window.innerWidth * RELATIVEWIDTH
    );

    this.dynamicBarChart.drawPlot(this.currentAnimationFrame);
  }
  updateDynamicScatterplot(rewardData: StepValueMap): void {
    this.dynamicBarChart.updateData(rewardData, this.currentAnimationFrame);
  }

  handleResize(e: any) {
    this.dynamicBarChart.setWidth(window.innerWidth * RELATIVEWIDTH);
    this.dynamicBarChart.drawPlot(this.currentAnimationFrame);
  }

  @Watch("currentAnimationFrame")
  public currentAnimationFrameChanged(newCurrentAnimationFrame: number): void {
    this.dynamicBarChart.drawPlot(newCurrentAnimationFrame);
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(): void {
    this.requestRewards();
  }

  mounted(): void {
    this.requestRewards();
  }

  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
