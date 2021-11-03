import {
  EpisodeValueMap,
  StepActionMap,
  StepCustomValMap,
  WeightMatrix,
} from "@/util/types";
import { VuexModule, Module, Mutation } from "vuex-module-decorators";

@Module({ namespaced: true, name: "Episode" })
export default class Episode extends VuexModule {
  public episodeRewards: EpisodeValueMap = {};
  public actionDivergences: EpisodeValueMap = {};

  public customBarChartCounter = 0;
  public customEpisodeBarCharts: Array<any> = [];
  public barChartLogTagList: Array<string> = [];
  public customEpisodeBarChartData: Array<StepCustomValMap> = [];

  @Mutation
  public setEpisodeRewards(episodeRewards: EpisodeValueMap): void {
    this.episodeRewards = episodeRewards;
  }

  @Mutation
  public setActionDivergences(actionDivergences: EpisodeValueMap): void {
    this.actionDivergences = actionDivergences;
  }

  @Mutation
  public setCustomBarChartCounter(barChartCounter: number): void {
    this.customBarChartCounter = barChartCounter;
  }

  @Mutation
  public setBarChartLogTagList(logTagList: Array<string>): void {
    this.barChartLogTagList = logTagList;
  }

  @Mutation
  public pushEpisodeBarChartData(
    customEpisodeBarChartData: StepCustomValMap
  ): void {
    this.customEpisodeBarChartData.push(customEpisodeBarChartData);
  }

  @Mutation
  public setEpisodeBarChartDataAt(
    i: number,
    customEpisodeBarChartData: StepCustomValMap
  ): void {
    this.customEpisodeBarChartData[i] = customEpisodeBarChartData;
  }
}
