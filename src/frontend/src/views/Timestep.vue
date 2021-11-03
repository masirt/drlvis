<template>
  <div class="timestep-container">
    <sub-heading heading="Timestep" />
    <h3 style="font-family: 'Open Sans Regular'; text-alignment: left">
      Selected Timestep
    </h3>
    <input
      type="number"
      min="0"
      :max="max"
      :value="currentAnimationFrame"
      @change="updateTimestep"
      class="timestep-selector"
    />
    <div class="view-content">
      <div class="view-charts">
        <action-prob-distribution class="action-chart chart" />
        <weights class="weight-hist" />
        <reward />
        <custom-timestep-chart
          v-for="customTChart in customTimestepCharts"
          :key="customTChart.id"
          :title="customTChart.title"
          :id="customTChart.id"
          :logTag="customTChart.logTag"
        />
        <v-dialog v-model="scalarDialog" scrollable max-width="300px">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="button" color="black" fab medium dark>
              <v-icon color="white" x-large v-bind="attrs" v-on="on"
                >mdi-plus</v-icon
              >
            </v-btn>
          </template>
          <v-card>
            <v-card-title>Select logging tag </v-card-title>
            <v-divider></v-divider>

            <v-card-text style="height: 300px">
              <v-text-field
                label="Chart Title"
                v-model="customChartTitle"
              ></v-text-field>
              <v-radio-group
                v-model="selectedTimestepLogTag"
                column
                label="Logged Tag"
              >
                <v-radio
                  v-for="logTag in timestepLogTagList"
                  :key="logTag"
                  :label="logTag"
                  :value="logTag"
                />
              </v-radio-group>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
              <v-btn color="black" text @click="scalarDialog = false">
                Close
              </v-btn>
              <v-btn color="black" text @click="addNewCustomTimestepData">
                Save
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
      <div class="video-container">
        <div class="video-view-container">
          <video-view />
        </div>
        <div class="slider-buttons">
          <v-slider
            v-model="slider"
            thumb-label
            :min="min"
            :max="max"
            hint="Timestep"
            persistent-hint
            style="width: 100%"
            color="#264653"
            track-color="lightgray"
          ></v-slider>

          <v-btn id="play-button" @click="this.togglePlay">Play</v-btn>
          <span></span>
          <v-btn id="playBackSpeed-button" @click="this.toggleSpeed"
            >x{{ playBackSpeed }}</v-btn
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import ActionProbDistribution from "./timestep-charts/ActionProbDistribution.vue";
import Weights from "./timestep-charts/Weights.vue";
import Reward from "./timestep-charts/Reward.vue";
import SubHeading from "./SubHeading.vue";
import CustomTimestepChart from "./timestep-charts/CustomTimestepChart.vue";

import VideoView from "./VideoView.vue";
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { CustomTimestepScalarData, StepActionMap } from "../util/types";
import { BASE_URL } from "../util/baseurl";
import * as d3 from "d3";
import { DynamicBarChart } from "../util/DynamicBarChart";
const general = namespace("General");
const timestep = namespace("Timestep");
export const RELATIVEWIDTH = 0.5 * 0.3;

@Component({
  components: {
    VideoView,
    ActionProbDistribution,
    Weights,
    Reward,
    SubHeading,
    CustomTimestepChart,
  },
})
export default class Timestep extends Vue {
  name: "Timestep";
  public interval: any;
  public playButton: any;
  public slider = 0;
  public min = 0;
  public max = 0;
  public playBackSpeed = 1;
  public selectedTimestepLogTag = "";
  public scalarDialog = false;
  public customChartTitle = "";

  @general.State
  public selectedEpisode: number;

  @general.State
  public hoveredEpisode: number;

  @general.State
  public currentAnimationFrame: number;

  @timestep.State
  public timestepLogTagList: Array<string>;

  @timestep.State
  public customTimestepChartCounter: number;

  @timestep.State
  public customTimestepCharts: Array<any>;

  @timestep.State
  public frameData: any;

  @timestep.State
  public probData: StepActionMap;

  @timestep.Mutation
  public setCustomTimestepChartCounter: (customCounter: number) => void;

  @timestep.Mutation
  public setTimestepLogTagList: (timestepLogTagList: Array<string>) => void;

  @general.Mutation
  public setSelectedEpisode: (selectedEpisode: number) => void;

  @general.Mutation
  public setCurrentAnimationFrame: (currentAnimationFrame: number) => void;

  @timestep.Mutation
  public setScaleMinMax: (scaleMinMax: boolean) => void;

  public updateTimestep(event: any) {
    if (event.target.value <= this.max && event.target.value >= 0) {
      this.setCurrentAnimationFrame(event.target.value);
      document
        .getElementsByClassName("timestep-selector")[0]
        .setAttribute("style", "border-color:lightgreen");
    } else {
      document
        .getElementsByClassName("timestep-selector")[0]
        .setAttribute("style", "border-color:red");
    }
  }

  addNewCustomTimestepData(): void {
    this.scalarDialog = false;

    this.customTimestepCharts.push({
      id: this.customTimestepChartCounter,
      title: this.customChartTitle,
      logTag: this.selectedTimestepLogTag,
    });
    this.setCustomTimestepChartCounter(this.customTimestepChartCounter + 1);
  }

  public toggleSpeed(): void {
    if (this.playBackSpeed == 1) {
      this.playBackSpeed++;
    } else if (this.playBackSpeed == 2) {
      this.playBackSpeed = 0.25;
    } else if (this.playBackSpeed < 1) {
      this.playBackSpeed += 0.5;
      if (this.playBackSpeed == 1.25) {
        this.playBackSpeed = 1;
      }
    }
  }

  public runInterval(): void {
    let dataRange = 0;

    if (this.frameData && this.frameData["frames"].length !== 0) {
      dataRange = this.frameData["frames"].length;
    } else {
      dataRange = Object.keys(this.probData).length;
    }

    if (this.currentAnimationFrame >= dataRange - 1) {
      this.setCurrentAnimationFrame(0);
    }
    this.setCurrentAnimationFrame(this.currentAnimationFrame + 1);
  }

  public togglePlay(): void {
    this.playButton = d3.select("#play-button");

    if (this.playButton.text() === "Pause") {
      if (this.interval) {
        clearInterval(this.interval);
        this.playButton.text("Play");
      }
    } else {
      clearInterval(this.interval);
      this.interval = setInterval(this.runInterval, 200 / this.playBackSpeed);
      this.playButton.text("Pause");
    }
  }

  requestTimestepLogTags() {
    (async () => {
      const logTagsResponce = await fetch(BASE_URL + "/get-timestep-log-tags", {
        method: "GET",
      });
      const logTags = await logTagsResponce.json();
      this.setTimestepLogTagList(logTags["timestepLogTags"]);
    })();
  }

  @Watch("selectedEpisode")
  public selectedEpisodeChanged(): void {
    if (this.playButton) this.playButton.text("Play");
    clearInterval(this.interval);
    this.setCurrentAnimationFrame(0);
    this.playBackSpeed = 1;
  }

  @Watch("frameData")
  public frameDataChanged(): void {
    this.slider = 0;
    this.min = 0;
    this.max = this.frameData["frames"].length - 1;
  }

  @Watch("probData")
  public probDataChanged(): void {
    if (!this.frameData) {
      const probDataRange: number = Object.keys(this.probData).length - 1;
      this.slider = 0;
      this.min = 0;
      this.max = probDataRange;
    }
  }

  @Watch("currentAnimationFrame")
  public currentAnimationFrameChanged(newCurrentAnimationFrame: number): void {
    this.slider = newCurrentAnimationFrame;
  }

  @Watch("slider")
  public sliderChanged(newSlider: number) {
    this.setCurrentAnimationFrame(newSlider);
  }

  @Watch("playBackSpeed")
  public playBackSpeedChanged(newPlayBackSpeed: number) {
    if (this.playButton && this.playButton.text() === "Pause") {
      clearInterval(this.interval);
      this.interval = setInterval(this.runInterval, 200 / newPlayBackSpeed);
    } else {
      return;
    }
  }

  mounted(): void {
    this.selectedEpisodeChanged();
  }

  beforeMount(): void {
    this.requestTimestepLogTags();
  }

  beforeDestroy(): void {
    clearInterval(this.interval);
  }
}
</script>

<style scoped>
.timestep-container {
  width: 100%;
  height: 100%;
  font-family: "Open Sans Regular";
}
.view-content {
  display: flex;
  flex-direction: row;
  border-top-left-radius: 1%;
  border-bottom-left-radius: 1%;
  height: 100%;
}

.view-charts {
  display: flex;
  flex-direction: column;
  height: 75%;
  width: 70%;
  min-width: 380px;
  padding-right: 5%;
  overflow-x: hidden;
  overflow-y: auto;
}

#play-button,
#playBackSpeed-button {
  margin-bottom: 2%;
  margin-top: 2%;
  width: 6%;
  height: 35px;
}
#playBackSpeed-button {
  margin-left: 3%;
}

.action-chart {
  padding: -10%;
}

.slider-buttons {
  margin-left: 0%;
}

.timestep-container {
  display: flex;
  flex-direction: column;
}

.video-container {
  display: flex;
  flex-direction: column;
  margin-left: 2%;
  width: 100%;
}

.video-view-container {
  display: block;
  position: relative;
  margin-top: -20%;
}

.icon-container-scatter {
  height: 80%;
  width: 50%;
  min-height: 30px;
  min-width: 280px;
  margin-left: 5%;
  margin-top: -3%;
  margin-bottom: 5%;
  text-align: center;
  border-style: dashed;
  border-width: 1px;
  border-color: #818a89;
  display: block;
  position: relative;
}

.icon-container-scatter:hover {
  transform: scale(1.1);
}

.plus-icon {
  position: absolute;
  top: 50%;
}
.button {
  margin: 0 auto;
  display: block;
}

.weight-hist {
  margin-top: 4%;
  margin-bottom: 4%;
}

.timestep-selector {
  width: 10%;
  height: 200px;
  padding: 1%;
  font-size: 36pt;
  text-align: center;
  border: 1%;
  border-radius: 5%;
  border-style: solid;
  border-color: #818a89;
}
</style>
