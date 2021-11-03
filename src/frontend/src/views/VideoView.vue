<template>
  <img
    style="width: 100%"
    v-if="frameData !== undefined"
    :src="'data:image/jpeg;base64,' + imageUrl"
  />
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { BASE_URL } from "../util/baseurl";

const general = namespace("General");
const timestep = namespace("Timestep");

@Component
export default class VideoView extends Vue {
  public imageUrl = "";
  public frameDataRange: number[];
  public interval: any;
  public playButton: any;
  public slider = 0;
  public min = 0;
  public max = 0;
  public playBackSpeed = 1;

  @general.State
  public selectedEpisode: number;

  @general.State
  public currentAnimationFrame: number;

  @timestep.State
  public frameData: any;

  @general.Mutation
  public setCurrentAnimationFrame: (currentAnimationFrame: number) => void;

  @timestep.Mutation
  public setFrameData: (frameData: unknown) => void;

  public setImageUrl(frameNum: number): void {
    try {
      this.imageUrl = this.frameData["frames"][frameNum];
    } catch (e) {
      if (this.interval) clearInterval(this.interval);
    }
  }

  requestFrames() {
    (async () => {
      const frameResponse = await fetch(
        BASE_URL + `/get-frames?user=${this.selectedEpisode}`,
        {
          method: "GET",
        }
      );

      const frameData = await frameResponse.json();
      if (frameData["frames"].length === 0) {
        console.log("No frames");
        return;
      }
      this.setFrameData(frameData);
      this.setImageUrl(0);
      this.slider = 0;
      this.min = 0;
      this.max = frameData["frames"].length - 1;
    })();
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged() {
    this.requestFrames();
  }

  @Watch("currentAnimationFrame")
  public currentAnimationFrameChanged(newCurrentAnimationFrame: number) {
    this.setImageUrl(newCurrentAnimationFrame);
  }

  @Watch("slider")
  public sliderChanged(newSlider: number) {
    this.setCurrentAnimationFrame(newSlider);
  }

  mounted() {
    this.requestFrames();
  }

  beforeDestroy() {
    clearInterval(this.interval);
  }
}
</script>
<style scoped>
#play-button {
  margin-bottom: 10px;
  margin-top: 10px;
}

img {
  border-radius: 3px;
  border: solid;
  border-color: black;
  border-width: 1px;
  margin-right: 30px;
}

span {
  margin-left: 20px;
}
</style>
