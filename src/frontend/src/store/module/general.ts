import { EpisodeValueMap } from "@/util/types";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";

@Module({ namespaced: true, name: "General" })
export default class General extends VuexModule {
  public selectedEpisode = 0;
  public currentAnimationFrame = 0;
  public currentPage = "Overview";
  public hoveredEpisode = -1;
  public customCounter = 0;
  public logTagList: Array<string> = [];
  public numberOfActions: number;

  public customEpisodeChartData: Array<EpisodeValueMap> = [];
  public customEpisodeCharts: Array<any> = [];

  @Mutation
  public setNumberOfActions(numberOfActions: number) {
    this.numberOfActions = numberOfActions;
  }

  @Mutation
  public setEpisodeChartDataAt(
    i: number,
    customEpisodeChartData: EpisodeValueMap
  ) {
    this.customEpisodeChartData[i] = customEpisodeChartData;
  }

  @Mutation
  public pushEpisodeChartData(customEpisodeChartData: EpisodeValueMap) {
    this.customEpisodeChartData.push(customEpisodeChartData);
  }

  @Mutation
  public setLogTagList(logTagList: Array<string>): void {
    this.logTagList = logTagList;
  }

  @Mutation
  public setSelectedEpisode(selectedEpisode: number): void {
    this.selectedEpisode = selectedEpisode;
  }

  @Mutation
  public setCurrentAnimationFrame(currentAnimationFrame: number): void {
    this.currentAnimationFrame = currentAnimationFrame;
  }

  @Mutation
  public setCurrentPage(currentPage: string): void {
    this.currentPage = currentPage;
  }

  @Mutation
  public setHoveredEpisode(hoveredEpisode: number): void {
    this.hoveredEpisode = hoveredEpisode;
  }

  @Mutation
  public setCustomCounter(customCounter: number) {
    this.customCounter = customCounter;
  }
}
