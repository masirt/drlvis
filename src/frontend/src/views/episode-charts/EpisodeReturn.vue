<template>
  <div id="episode-reward-chart" />
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { BASE_URL } from "../../util/baseurl";
import { ScatterPlot } from "../../util/ScatterPlot";
import { EpisodeValueMap } from "../../util/types";
import { RELATIVEEPWIDTH } from "../Episode.vue";

const general = namespace("General");
const episode = namespace("Episode");

@Component
export default class EpisodeReward extends Vue {
  name: "EpisodeReward";

  public scatterPlot: ScatterPlot;

  @general.State
  public selectedEpisode: number;

  @general.State
  public hoveredEpisode: number;

  @episode.State
  public episodeRewards: EpisodeValueMap;

  @episode.Mutation
  public setEpisodeRewards: (episodeRewards: EpisodeValueMap) => void;

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

  handleResize(e: any) {
    this.scatterPlot.setWidth(window.innerWidth * RELATIVEEPWIDTH);
    this.scatterPlot.drawScatterPlot(
      "" + this.selectedEpisode,
      "" + this.hoveredEpisode
    );
  }

  beforeMount() {
    (async () => {
      const episodeRewardsResponse = await fetch(
        BASE_URL + "/episode-rewards",
        {
          method: "GET",
        }
      );
      const episodeRewards = await episodeRewardsResponse.json();
      this.setEpisodeRewards(episodeRewards);

      this.scatterPlot = new ScatterPlot(
        this.episodeRewards,
        "episode-reward-chart",
        "Episode Returns",
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
