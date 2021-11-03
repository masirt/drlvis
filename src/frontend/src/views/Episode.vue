<template>
  <div class="episode-container">
    <div class="view-container">
      <sub-heading heading="Episode" />
      <div class="view-content">
        <div class="view-column-1">
          <h3 style="font-family: 'Open Sans Regular'; text-alignment: left">
            Selected Episode
          </h3>
          <input
            type="number"
            min="0"
            :max="maxEpisode"
            :value="selectedEpisode"
            @change="updateEpisode"
            class="episode-selector"
          />
          <action-distribution />
          <custom-episode-bar-chart
            v-for="customChart in customEpisodeBarCharts"
            :key="customChart.id"
            :title="customChart.title"
            :id="customChart.id"
            :logTag="customChart.logTag"
          />
          <v-dialog v-model="dialogBarChart" scrollable max-width="300px">
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
                  v-model="customBarChartTitle"
                ></v-text-field>

                <v-radio-group
                  v-model="selectedBarChartLogTag"
                  column
                  label="Logged Tag"
                >
                  <v-radio
                    v-for="logTag in barChartLogTagList"
                    :key="logTag"
                    :label="logTag"
                    :value="logTag"
                  />
                </v-radio-group>
              </v-card-text>
              <v-divider></v-divider>
              <v-card-actions>
                <v-btn color="black" text @click="dialogBarChart = false">
                  Close
                </v-btn>
                <v-btn color="black" text @click="addNewCustomBarChartData">
                  Save
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </div>
        <div class="view-column-2">
          <episode-return class="chart" />
          <action-divergence class="chart" />
          <custom-episode-chart
            v-for="customEpChart in customEpisodeCharts"
            :key="customEpChart.id"
            :title="customEpChart.title"
            :id="customEpChart.id"
            :logTag="customEpChart.logTag"
          />
          <v-dialog v-model="dialog" scrollable max-width="300px">
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
                  v-model="selectedLogTag"
                  column
                  label="Logged Tag"
                >
                  <v-radio
                    v-for="logTag in logTagList"
                    :key="logTag"
                    :label="logTag"
                    :value="logTag"
                  />
                </v-radio-group>
              </v-card-text>
              <v-divider></v-divider>
              <v-card-actions>
                <v-btn color="black" text @click="dialog = false">
                  Close
                </v-btn>
                <v-btn color="black" text @click="addNewCustomData">
                  Save
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import EpisodeReturn from "./episode-charts/EpisodeReturn.vue";
import ActionDivergence from "./episode-charts/ActionDivergence.vue";
import ActionDistribution from "./episode-charts/ActionDistribution.vue";
import SubHeading from "./SubHeading.vue";
import CustomChartDialogueCard from "./CustomChartDialogueCard.vue";
import CustomEpisodeChart from "./episode-charts/CustomEpisodeChart.vue";
import CustomEpisodeBarChart from "./episode-charts/CustomEpisodeBarChart.vue";

import { Component, Vue, Watch } from "vue-property-decorator";
import { namespace } from "vuex-class";

import { EpisodeValueMap } from "../util/types";
import { BASE_URL } from "../util/baseurl";
const general = namespace("General");
const episode = namespace("Episode");
export const RELATIVEEPWIDTH = 0.5 * 0.65;
export const RELATIVEEPDISTWIDTH = 0.5 * 0.15;
@Component({
  components: {
    EpisodeReturn,
    ActionDivergence,
    ActionDistribution,
    SubHeading,
    CustomChartDialogueCard,
    CustomEpisodeChart,
    CustomEpisodeBarChart,
  },
})
export default class Episode extends Vue {
  name: "Overview";
  public interval: any;
  public maxEpisode = 0;
  public dialog = false;
  public selectedLogTag = "";
  public customChartTitle = "";

  public dialogBarChart = false;
  public selectedBarChartLogTag = "";
  public customBarChartTitle = "";

  @general.State
  public logTagList: Array<string>;

  @general.State
  public customCounter: number;

  @general.State
  public selectedEpisode: number;

  @general.State
  public hoveredEpisode: number;

  @general.State
  public customEpisodeCharts: Array<any>;

  @episode.State
  public episodeRewards: EpisodeValueMap;

  @episode.State
  public actionDivergences: EpisodeValueMap;

  @episode.State
  public barChartLogTagList: Array<string>;

  @episode.State
  public customBarChartCounter: number;

  @episode.State
  public customEpisodeBarCharts: Array<any>;

  @general.Mutation
  public setLogTagList: (logTagList: Array<string>) => void;

  @general.Mutation
  public setCustomCounter: (customCounter: number) => void;

  @general.Mutation
  public setSelectedEpisode: (selectedEpisode: number) => void;

  @episode.Mutation
  public setBarChartLogTagList: (logTagList: Array<string>) => void;

  @episode.Mutation
  public setCustomBarChartCounter: (barChartCounter: number) => void;

  public updateEpisode(event: any) {
    if (event.target.value <= this.maxEpisode && event.target.value >= 0) {
      this.setSelectedEpisode(event.target.value);
      document
        .getElementsByClassName("episode-selector")[0]
        .setAttribute("style", "border-color:lightgreen");
    } else {
      document
        .getElementsByClassName("episode-selector")[0]
        .setAttribute("style", "border-color:red");
    }
  }

  public addNewCustomData(): void {
    this.dialog = false;

    this.customEpisodeCharts.push({
      id: this.customCounter,
      title: this.customChartTitle,
      logTag: this.selectedLogTag,
    });
    this.setCustomCounter(this.customCounter + 1);
  }

  public addNewCustomBarChartData(): void {
    this.dialogBarChart = false;

    this.customEpisodeBarCharts.push({
      id: this.customBarChartCounter,
      title: this.customBarChartTitle,
      logTag: this.selectedBarChartLogTag,
    });

    this.setCustomBarChartCounter(this.customBarChartCounter + 1);
  }

  public requestLogTags(): void {
    (async () => {
      const logTagsResponce = await fetch(BASE_URL + "/get-log-tags", {
        method: "GET",
      });
      const logTags = await logTagsResponce.json();
      this.setLogTagList(logTags["logTags"]);
    })();
  }

  public requestBarChartLogTags(): void {
    (async () => {
      const logTagsResponce = await fetch(
        BASE_URL + "/get-distribution-log-tags",
        {
          method: "GET",
        }
      );
      const logTags = await logTagsResponce.json();
      this.setBarChartLogTagList(logTags["logTags"]);
    })();
  }

  @Watch("episodeRewards")
  public episodeRewardsChanged() {
    this.maxEpisode = Object.keys(this.episodeRewards).length - 1;
  }

  @Watch("actionDivergences")
  public actionDivergencesChanged() {
    this.maxEpisode = Object.keys(this.actionDivergences).length;
  }

  beforeMount() {
    this.requestLogTags();
    this.requestBarChartLogTags();
  }
}
</script>
<style>
.episode-container {
  display: flex;
  flex-direction: row;
  margin-left: 1%;
  height: 100%;
  width: 100%;
}

.view-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.view-content {
  display: flex;
  flex-direction: row;
  height: 100%;
}

.view-column-1 {
  width: 20%;
}

.view-column-2 {
  display: flex;
  flex-direction: column;
  height: 85%;
  overflow-x: hidden;
  overflow-y: auto;
}

.episode-selector {
  width: 70%;
  height: 100px;
  font-size: 36pt;
  margin-top: 2%;
  text-align: center;
  border: 1%;
  border-radius: 5%;
  border-style: solid;
  border-color: #818a89;
}

.icon-container {
  height: 100%;
  width: 80%;
  min-height: 100px;
  margin-left: 10%;
  text-align: center;
  border-style: dashed;
  border-width: 1px;
  border-color: #818a89;
  display: block;
  position: relative;
  font-family: "Open Sans Regular";
}

.icon-container-barchart {
  height: 5%;
  width: 70%;
  min-height: 30px;
  margin-top: -15%;
  margin-left: 20%;
  text-align: center;
  border-style: dashed;
  border-width: 1px;
  border-color: #818a89;
  display: block;
  position: relative;
}

.plus-icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.icon-container:hover,
.icon-container-barchart:hover {
  transform: scale(1.1);
}

.chart {
  background: white;
  border-width: 1px;
  border: lightgray;
  border-radius: 2%;
  margin-left: 2%;
  margin-top: 1%;
}

.button {
  margin: 0 auto;
  display: block;
}

body {
  font-family: "Open Sans Regular";
}
</style>
