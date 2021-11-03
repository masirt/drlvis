import { StepActionMap, StepValueMap, WeightMatrix } from "@/util/types";
import { VuexModule, Module, Mutation } from "vuex-module-decorators";

@Module({ namespaced: true, name: "Timestep" })
export default class Timestep extends VuexModule {
  public frameData = null;
  public rewardData: StepValueMap = {};
  public probData: StepActionMap = {};
  public actionDistributionData: StepActionMap = {};
  public weightMatrix: WeightMatrix = {};
  public actionMeanings: string[] = [];
  public scaleMinMax = false;
  public selectedTimeStep = 0;
  public hoveredTimeStep = -1;

  public timestepLogTagList: Array<string> = [];
  public customTimestepChartData: Array<StepValueMap> = [];
  public customTimestepCharts: Array<any> = [];
  public customTimestepChartCounter = 0;

  @Mutation
  public setCustomTimestepChartCounter(customCounter: number) {
    this.customTimestepChartCounter = customCounter;
  }

  @Mutation
  public setTimestepChartDataAt(
    i: number,
    customTimestepChartData: StepValueMap
  ) {
    this.customTimestepChartData[i] = customTimestepChartData;
  }

  @Mutation
  public pushTimestepChartData(customTimestepChartData: StepValueMap) {
    this.customTimestepChartData.push(customTimestepChartData);
  }

  @Mutation
  public setTimestepLogTagList(timestepLogTagList: Array<string>) {
    this.timestepLogTagList = timestepLogTagList;
  }

  @Mutation
  public setRewardData(rewardData: StepValueMap) {
    this.rewardData = rewardData;
  }

  @Mutation
  public setFrameData(frameData: any): void {
    this.frameData = frameData;
  }

  @Mutation
  public setProbData(probData: StepActionMap): void {
    this.probData = probData;
  }

  @Mutation
  public setActionDistributionData(
    actionDistributionData: StepActionMap
  ): void {
    this.actionDistributionData = actionDistributionData;
  }

  @Mutation
  public setWeightMatrix(weightMatrix: WeightMatrix): void {
    this.weightMatrix = weightMatrix;
  }

  @Mutation
  public setActionMeanings(actionMeanings: string[]): void {
    this.actionMeanings = actionMeanings;
  }

  @Mutation
  public setScaleMinMax(scaleMinMax: boolean): void {
    this.scaleMinMax = scaleMinMax;
  }
}
