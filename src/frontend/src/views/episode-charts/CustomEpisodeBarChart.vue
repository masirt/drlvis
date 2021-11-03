<template>
  <div :id="'custom-episode-bar-chart-' + id"></div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { CustomBarChart } from "../../util/CustomBarChart";
import { StepCustomValMap } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEEPDISTWIDTH } from "../Episode.vue";

const general = namespace("General");
const episode = namespace("Episode");

@Component
export default class CustomEpisodeBarChart extends Vue {
  name: "CustomEpisodeBarChart";

  @Prop()
  public id: number;

  @Prop()
  public title: string;

  @Prop()
  public logTag: string;

  public barChart: CustomBarChart;

  @general.State
  public selectedEpisode: number;

  @episode.State
  public customEpisodeBarChartData: Array<StepCustomValMap>;

  @episode.Mutation
  public pushEpisodeBarChartData: (
    customEpisodeBarChartData: StepCustomValMap
  ) => void;

  @episode.Mutation
  public setEpisodeBarChartDataAt: (
    i: number,
    customEpisodeBarChartData: StepCustomValMap
  ) => void;

  createBarChart(customBarChartData: StepCustomValMap): void {
    const values: number[] = [];
    Object.values(customBarChartData).forEach((elem: StepCustomValMap) => {
      Object.values(elem).forEach((elem) => values.push(elem.value));
    });
    const maxBound = Math.max(...values);
    this.barChart = new CustomBarChart(
      customBarChartData,
      `custom-episode-bar-chart-${this.id}`,
      [0, maxBound],
      this.title,
      window.innerWidth * RELATIVEEPDISTWIDTH,
      30
    );
    this.barChart.drawBarChart(this.selectedEpisode);
  }

  requestCustomBarChartData(): void {
    (async () => {
      const customChartsDataResponse = await fetch(
        BASE_URL + "/get-custom-distribution?user=" + this.logTag,
        {
          method: "GET",
        }
      );
      const customChartsData: StepCustomValMap = await customChartsDataResponse.json();

      this.pushEpisodeBarChartData(customChartsData);
      this.createBarChart(customChartsData);
    })();
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(newSelectedEpisode: number): void {
    this.barChart.drawBarChart(newSelectedEpisode);
  }

  mounted() {
    this.requestCustomBarChartData();
  }
  handleResize(e: any) {
    this.barChart.setWidth((window.innerWidth / 2) * 0.15);
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
