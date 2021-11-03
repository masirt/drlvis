<template>
  <div :id="'custom-episode-chart-' + id"></div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { ScatterPlot } from "../../util/ScatterPlot";
import { EpisodeValueMap } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEEPWIDTH } from "../Episode.vue";

const general = namespace("General");

@Component
export default class CustomEpisodeChart extends Vue {
  name: "CustomEpisodeChart";

  @Prop()
  public id: number;

  @Prop()
  public title: string;

  @Prop()
  public logTag: string;

  public scatterPlot: ScatterPlot;

  @general.State
  public selectedEpisode: number;

  @general.State
  public hoveredEpisode: number;

  @general.State
  public customEpisodeChartData: Array<EpisodeValueMap>;

  @general.Mutation
  public pushEpisodeChartData: (
    customEpisodeChartData: EpisodeValueMap
  ) => void;

  @general.Mutation
  public setEpisodeChartDataAt: (
    i: number,
    customEpisodeChartData: EpisodeValueMap
  ) => void;

  mounted(): void {
    (async () => {
      const customChartsDataResponse = await fetch(
        BASE_URL + "/get-tag-scalars?user=" + this.logTag,
        {
          method: "GET",
        }
      );
      const customChartsData: EpisodeValueMap = await customChartsDataResponse.json();

      this.pushEpisodeChartData(customChartsData);

      this.scatterPlot = new ScatterPlot(
        customChartsData,
        `custom-episode-chart-${this.id}`,
        this.title,
        window.innerWidth * RELATIVEEPWIDTH
      );

      this.scatterPlot.drawScatterPlot(
        "" + this.selectedEpisode,
        "" + this.hoveredEpisode
      );
    })();
  }

  handleResize(e: any) {
    this.scatterPlot.setWidth(window.innerWidth * RELATIVEEPWIDTH);
    this.scatterPlot.drawScatterPlot(
      "" + this.selectedEpisode,
      "" + this.hoveredEpisode
    );
  }
  @Watch("selectedEpisode")
  public selectedEpisodeChanged(newSelectedEpisode: number): void {
    this.scatterPlot.drawScatterPlot(
      "" + newSelectedEpisode,
      "" + this.hoveredEpisode
    );
  }

  @Watch("hoveredEpisode")
  public hoveredEpisodeChanged(newHoveredEpisode: number): void {
    this.scatterPlot.drawScatterPlot(
      "" + this.selectedEpisode,
      "" + newHoveredEpisode
    );
  }

  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
