<template>
  <div :id="'custom-timestep-chart-' + id"></div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { DynamicBarChart } from "../../util/DynamicBarChart";
import { StepValueMap } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEWIDTH } from "../Timestep.vue";

const general = namespace("General");
const timestep = namespace("Timestep");

@Component
export default class CustomTimestepChart extends Vue {
  name: "CustomEpisodeChart";

  @Prop()
  public id: number;

  @Prop()
  public title: string;

  @Prop()
  public logTag: string;

  public scatterPlot: DynamicBarChart;
  public scatterPlotCreated = false;

  @general.State
  public selectedEpisode: number;

  @general.State
  public currentAnimationFrame: number;

  @timestep.State
  public customTimestepChartData: Array<StepValueMap>;

  @timestep.State
  public customTimestepCharts: Array<any>;

  @timestep.Mutation
  public setTimestepChartDataAt: (
    i: number,
    customTimestepChartData: StepValueMap
  ) => void;

  @timestep.Mutation
  public pushTimestepChartData: (customTimestepChartData: StepValueMap) => void;

  requestTimestepChartData(): void {
    (async () => {
      let customChartsData: StepValueMap = {};

      if (!this.customTimestepChartData[this.selectedEpisode]) {
        const customChartsDataResponse = await fetch(
          BASE_URL +
            "/get-tag-scalars?user=" +
            this.logTag +
            "-e" +
            this.selectedEpisode,
          {
            method: "GET",
          }
        );
        customChartsData = await customChartsDataResponse.json();
      } else {
        customChartsData = this.customTimestepChartData[this.selectedEpisode];
      }

      if (this.scatterPlotCreated) {
        this.updateScatterplot(customChartsData);
      } else {
        this.scatterPlotCreated = true;
        this.createScatterplot(customChartsData);
      }
    })();
  }

  createScatterplot(customChartsData: StepValueMap): void {
    this.scatterPlot = new DynamicBarChart(
      customChartsData,
      `custom-timestep-chart-${this.id}`,
      this.title,
      window.innerWidth * RELATIVEWIDTH
    );
    this.scatterPlot.drawPlot(this.currentAnimationFrame);
  }

  updateScatterplot(customChartsData: StepValueMap): void {
    this.scatterPlot.updateData(customChartsData, this.currentAnimationFrame);
    //if (this.scatterPlot) this.scatterPlot.drawPlot(this.currentAnimationFrame);
  }

  @Watch("currentAnimationFrame")
  public currentAnimationFrameChanged(newCurrentAnimationFrame: number): void {
    if (this.scatterPlot) this.scatterPlot.drawPlot(newCurrentAnimationFrame);
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(): void {
    this.requestTimestepChartData();
  }

  handleResize(e: any) {
    this.scatterPlot.setWidth(window.innerWidth * RELATIVEWIDTH);
    this.scatterPlot.drawPlot(this.currentAnimationFrame);
  }

  mounted(): void {
    this.requestTimestepChartData();
  }

  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
