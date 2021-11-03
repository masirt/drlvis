<template>
  <div id="action-divergence-chart" />
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { ScatterPlot } from "../../util/ScatterPlot";
import { EpisodeValueMap } from "../../util/types";
import { BASE_URL } from "../../util/baseurl";
import { RELATIVEEPWIDTH } from "../Episode.vue";

const general = namespace("General");
const episode = namespace("Episode");

@Component
export default class ActionDivergence extends Vue {
  name: "ActionDivergence";

  public scatterPlot: ScatterPlot;

  @general.State
  public selectedEpisode: number;

  @general.State
  public hoveredEpisode: number;

  @episode.State
  public actionDivergences: EpisodeValueMap;

  @episode.Mutation
  public setActionDivergences: (actionDivergences: EpisodeValueMap) => void;

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
  public hoveredEpisodeChanges(newHoveredEpisode: number): void {
    this.scatterPlot.drawScatterPlot(
      "" + this.selectedEpisode,
      "" + newHoveredEpisode
    );
  }

  beforeMount() {
    (async () => {
      const actionDivergencesResponse = await fetch(
        BASE_URL + "/action-divergences",
        {
          method: "GET",
          mode: "cors",
        }
      );
      const actionDivergences = await actionDivergencesResponse.json();
      this.setActionDivergences(actionDivergences);

      this.scatterPlot = new ScatterPlot(
        this.actionDivergences,
        "action-divergence-chart",
        "Action Divergence",
        window.innerWidth * RELATIVEEPWIDTH
      );
      this.scatterPlot.drawScatterPlot(
        "" + this.selectedEpisode,
        "" + this.hoveredEpisode
      );
    })();
  }
  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
<style scoped></style>
