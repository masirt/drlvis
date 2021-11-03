import store from "../store/index";

export interface EpisodeValueMap {
  [episode: number]: [value: number, mean: number];
}

export interface StepValueMap {
  [step: number]: [value: number, mean: number];
}

export interface StepCustomValMap {
  [step: number]: CustomVal[];
}

export interface StepActionMap {
  [step: number]: Action[];
}

export interface Action {
  name: string;
  value: number;
}

export interface CustomVal {
  name: string;
  value: number;
}

export interface ExperimentalEpisodeArrayMap {
  [episode: number]: number[][];
}

export interface ExperimentalMap {
  minEpisode: number;
  maxEpisode: number;
  step: number;
  minState: number[];
  maxState: number[];
  values: number[][];
}

export interface EpisodeArrayMap {
  [episode: number]: [values: number[]];
}

export interface WeightMatrix {
  [episode: number]: WeightObject[];
}

export interface WeightObject {
  [index: string]: number;
}

export interface CustomChartData {
  title: string;
  logTag: string;
  data: EpisodeValueMap;
}

export interface CustomTimestepScalarData {
  title: string;
  logTag: string;
  data: StepValueMap;
}

export type State = typeof store.state;
