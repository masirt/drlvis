import { ExperimentalMap, StepActionMap, WeightMatrix } from "@/util/types";
import { VuexModule, Module, Mutation } from "vuex-module-decorators";

@Module({ namespaced: true, name: "Confidence" })
export default class Confidence extends VuexModule {
  public experimentalMap: ExperimentalMap;
  public currentEpisode = 0;
  public isNoImageData = true;
  public dataTypeNotSelected = true;

  @Mutation
  public setDataTypeNotSelected(dataTypeNotSelected: boolean) {
    this.dataTypeNotSelected = dataTypeNotSelected;
  }

  @Mutation
  public setIsNoImageData(isNoImageData: boolean) {
    this.isNoImageData = isNoImageData;
  }

  @Mutation
  public setExperimentalMap(experimentalMap: ExperimentalMap): void {
    this.experimentalMap = experimentalMap;
  }

  @Mutation
  public setCurrentEpisode(currentEpisode: number): void {
    this.currentEpisode = currentEpisode;
  }
}
