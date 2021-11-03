<template>
  <div style="width: 100%">
    <div class="confidence-container">
      <div class="confidence-chart-container">
        <div class="chart-view">
          <div id="confidence-state-action-chart" />
          <v-slider
            v-model="slider"
            tickSize="4"
            :min="min"
            :max="max"
            :step="step"
            hint="Episode"
            thumb-label="always"
            persistent-hint
            class="slider"
            color="black"
            track-color="lightgray"
          ></v-slider>
        </div>
        <div class="headerbar">
          <sub-heading :heading="'Confidence Chart'" />
          <span style="height: 10px" />
          <h3 class="heading-legends">Confidence in selecting actions</h3>
          <div v-if="actionMeanings">
            <div
              v-for="(actionMeaning, i) in actionMeanings"
              :key="actionMeaning"
              class="action-Legend"
            >
              <div class="legend-text">
                <div class="textlow">Low Confidence</div>
                <span class="high-low-divider-span"></span>
                <div class="texthigh">High Confidence</div>
              </div>
              <div
                class="legend-bar"
                :style="
                  'background-image: linear-gradient(to right,' +
                  colorPalette[i] +
                  '40' +
                  ',' +
                  colorPalette[i] +
                  ')'
                "
              >
                {{ actionMeaning }}
              </div>
            </div>
          </div>
          <div v-else>
            <div
              v-for="index in numberOfActions"
              :key="index"
              class="action-Legend"
            >
              <div class="legend-text">
                <div class="textlow">Low Confidence</div>
                <span class="high-low-divider-span"></span>
                <div class="texthigh">High Confidence</div>
              </div>
              <div
                class="legend-bar"
                :style="
                  'background-image: linear-gradient(to right,' +
                  colorPalette[index - 1] +
                  '40' +
                  ',' +
                  colorPalette[index - 1] +
                  ')'
                "
              >
                {{ "action " + (index - 1) }}
              </div>
            </div>
          </div>
          <span style="height: 30px" />

          <div v-if="isNoImageData && experimentalMap" class="minmaxstatebar">
            <h3>Maximum State Values</h3>
            <div class="maxmin-state-values">
              <div
                v-for="maxStateVal in experimentalMap.maxState"
                :key="maxStateVal"
                style="margin-right: 10%"
              >
                {{ Math.round((maxStateVal + Number.EPSILON) * 100) / 100 }}
              </div>
            </div>
            <h3>Minimum State Values</h3>
            <div class="maxmin-state-values">
              <div
                v-for="minStateVal in experimentalMap.minState"
                :key="minStateVal"
                style="margin-right: 10%"
              >
                {{ Math.round((minStateVal + Number.EPSILON) * 100) / 100 }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- </div>
    <div v-else>
      <v-dialog v-model="dataTypeNotSelected" max-width="290">
        <v-card>
          <v-card-title class="text-h5">
            Did your task involve images as input data or not?
          </v-card-title>

          <v-card-text>
            This interface looks different for tasks where image data was
            involved than for tasks where no image data was used. That is why
            you have to select which of the two applies for you.
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn
              color="#264653"
              text
              @click="
                () => {
                  this.setIsNoImageData(true);
                  this.setDataTypeNotSelected(false);
                  this.createChart();
                }
              "
            >
              No Image Data
            </v-btn>

            <v-btn
              color="#264653"
              text
              @click="
                () => {
                  this.setIsNoImageData(false);
                  this.setDataTypeNotSelected(false);
                  this.createChart();
                }
              "
            >
              Image Data
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div> -->
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { ExperimentalScatterplot } from "../../util/ExperimentalScatterPlot";
import SubHeading from "../SubHeading.vue";
import { ExperimentalMap } from "../../util/types";

import { BASE_URL } from "../../util/baseurl";
import * as d3 from "d3";
import { getColorPalette } from "../../util/colorpalette";
const confidence = namespace("Confidence");
const general = namespace("General");
const timestep = namespace("Timestep");

const RELATIVECONFCHARTWIDTH = 0.75;

const RELATIVECONFCHARTHEIGHT = 0.65;

@Component({
  components: { SubHeading },
})
export default class Confidence extends Vue {
  name: "Confidence";
  public experimentalScatterPlot: ExperimentalScatterplot;

  public slider = 0;
  public min = 0;
  public max = 0;
  public step = 1;
  public tickLabels: string[] = [];
  public colorPalette = getColorPalette();

  @timestep.State
  public actionMeanings: string[];

  @general.State
  public numberOfActions: number;

  @confidence.State
  public currentEpisode: number;

  @confidence.State
  public isNoImageData: boolean;

  @confidence.State
  public experimentalMap: ExperimentalMap;

  @confidence.State
  public dataTypeNotSelected: boolean;

  @confidence.Mutation
  public setDataTypeNotSelected: (dataTypeNotSelected: boolean) => void;

  @confidence.Mutation
  public setIsNoImageData: (isNoImageData: boolean) => void;

  @confidence.Mutation
  public setExperimentalMap: (experimentalMap: ExperimentalMap) => void;

  @confidence.Mutation
  public setCurrentEpisode: (episode: number) => void;

  @Watch("currentEpisode")
  public currentEpisodeChanged(newCurrentEpisode: number): void {
    (async () => {
      const experimentalMapResponse = await fetch(
        BASE_URL +
          `/get-experiment-random-states-data?user=${newCurrentEpisode}`,
        {
          method: "GET",
        }
      );

      const experimentalMap = await experimentalMapResponse.json();
      this.setExperimentalMap(experimentalMap);

      this.experimentalScatterPlot.drawScatterPlot(
        experimentalMap,
        newCurrentEpisode
      );
    })();
  }

  @Watch("slider")
  sliderChanged(newSlider: number): void {
    this.setCurrentEpisode(newSlider);
  }

  createChart() {
    (async () => {
      const firstConfExpEpisodeResponse = await fetch(
        BASE_URL + `/get-confidence-exp-first-episode`,
        {
          method: "GET",
        }
      );
      const episode: number | unknown = Object.values(
        await firstConfExpEpisodeResponse.json()
      )[0];
      this.setCurrentEpisode(Number(episode));

      const experimentalMapResponse = await fetch(
        BASE_URL +
          `/get-experiment-random-states-data?user=${this.currentEpisode}`,
        {
          method: "GET",
        }
      );

      const experimentalMap = await experimentalMapResponse.json();

      this.setExperimentalMap(experimentalMap);

      this.experimentalScatterPlot = new ExperimentalScatterplot(
        experimentalMap,
        "confidence-state-action-chart",
        window.innerWidth * RELATIVECONFCHARTWIDTH,
        window.innerHeight * RELATIVECONFCHARTHEIGHT
      );

      d3.select(".slider").attr(
        "width",
        (window.innerWidth * RELATIVECONFCHARTWIDTH) / 2
      );

      this.max = experimentalMap.maxEpisode;
      this.min = experimentalMap.minEpisode;
      this.step = experimentalMap.step !== 0 ? experimentalMap.step : 1;
      for (let i = this.min; i <= this.max; i = i + this.step) {
        this.tickLabels.push("" + i);
      }

      this.experimentalScatterPlot.drawScatterPlot(
        experimentalMap,
        this.currentEpisode
      );
      this.setIsNoImageData(
        experimentalMap.minState[0] != 0 && experimentalMap.maxState[0] != 0
      );
    })();
  }

  mounted(): void {
    this.createChart();
  }
  handleResize(e: any) {
    d3.select(".slider").attr(
      "width",
      (window.innerWidth * RELATIVECONFCHARTWIDTH) / 2
    );
    this.experimentalScatterPlot.setWidthandHeight(
      window.innerWidth * RELATIVECONFCHARTWIDTH,
      window.innerHeight * RELATIVECONFCHARTHEIGHT
    );

    this.experimentalScatterPlot.drawScatterPlot(
      this.experimentalMap,
      this.currentEpisode
    );

    d3.selectAll(".legend-bar").attr("width", window.innerWidth / 2);
  }

  created() {
    window.addEventListener("resize", this.handleResize);
  }

  destroyed() {
    window.removeEventListener("resize", this.handleResize);
  }
}
</script>
<style scoped>
body {
  font-family: "Open Sans Regular";
}

.slider {
  overflow: auto;
  min-height: 50px;
  padding-top: 50px;
  padding: 50px;
  margin-bottom: 50px;
}
.confidence-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.confidence-chart-container {
  display: flex;
  flex-direction: row;
}

.headerbar {
  display: flex;
  flex-direction: column;
  overflow-y: scroll;
  background: #f8f8f8;
  width: 100%;
  padding-left: 0.5%;
}

.maxmin-state-values {
  display: flex;
  flex-direction: row;
}

.legend-bar {
  width: 95%;
  height: 30px;
  text-align: center;
  color: black;
  /* background-image: linear-gradient(to left, #fbb4ae, #fbb4ae20);*/
}
.legend-text {
  display: flex;
  flex-direction: row;
}

.minmaxstatebar {
  overflow-x: scroll;
}

.high-low-divider-span {
  width: 45%;
}
</style>
