import * as d3 from "d3";
import { StepActionMap, Action } from "./types";
import store from "../store/index";
import { NumberValue } from "d3";
import { getColorPalette } from "./colorpalette";
export class BarChart {
  stepData: StepActionMap;
  margin = { top: 40, right: 20, bottom: 50, left: 45 };
  width = 300;
  barHeight = 30;
  height: number;
  svg: d3.Selection<SVGSVGElement, unknown, HTMLElement | null, undefined>;
  mainGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xScale: d3.ScaleLinear<number, number>;
  yScale: d3.ScaleBand<string>;
  colors: string[];
  xAxisGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  yAxisGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xAxis: d3.Axis<NumberValue>;
  yAxis: d3.Axis<string>;
  withNames: boolean;
  bounds: number[];
  actionToNumber: any;

  constructor(
    stepData: StepActionMap,
    domElementId: string,
    bounds: number[],
    title: string,
    width: number,
    barHeight: number
  ) {
    this.stepData = stepData;
    if (Object.keys(this.stepData).length == 0) return;

    this.withNames = store.state.Timestep.actionMeanings !== undefined;

    const yDomain: string[] = [];
    if (width) this.width = width;
    if (barHeight) this.barHeight = barHeight;
    this.actionToNumber = {};
    stepData[0].forEach((element: Action, index) => {
      yDomain.push(
        this.withNames
          ? store.state.Timestep.actionMeanings[index]
          : element.name
      );
      this.actionToNumber[element.name] = index;
    });
    store.state.General.numberOfActions = yDomain.length;

    this.colors = getColorPalette();
    this.height = this.barHeight * stepData[0].length;

    this.bounds = bounds;
    this.xScale = d3
      .scaleLinear()
      .domain([bounds[1], bounds[0]])
      .range([this.width, 0]);

    this.yScale = d3
      .scaleBand()
      .domain(yDomain)
      .range([this.height, 0])
      .padding(0.1);

    this.xAxis = d3.axisBottom(this.xScale);
    this.yAxis = d3.axisLeft(this.yScale).ticks(5);

    this.svg = d3
      .select(`#${domElementId}`)
      .append("svg")
      .attr("width", this.width + this.margin.left + this.margin.right)
      .attr("height", this.height + this.margin.top + this.margin.bottom);

    this.mainGroup = this.svg
      .append("g")
      .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

    this.svg
      .append("text")
      .attr("x", 0)
      .attr("y", this.margin.top / 2)
      .attr("text-anchor", "left")
      .style("font-size", "14px")
      .style("font-family", "Open Sans Regular")
      .text(`${title}`);

    const chart: any = d3.select(`#${domElementId}`);
  }

  setWidth(width: number) {
    if (Object.keys(this.stepData).length == 0) return;
    this.width = width;
    this.svg.attr("width", this.width + this.margin.left + this.margin.right);
  }

  drawBarChart(stepCount: number): void {
    if (Object.keys(this.stepData).length == 0) return;
    const data = this.stepData[stepCount];

    this.xScale = d3
      .scaleLinear()
      .domain([this.bounds[1], this.bounds[0]])
      .range([this.width, 0]);
    this.xAxis = d3.axisBottom(this.xScale);

    const tooltip = d3
      .select("body")
      .append("div")
      .attr("id", "tooltip")
      .attr("style", "position: absolute; opacity:0;")
      .style("background-color", "white")
      .style("border", "solid")
      .style("border-width", "2px")
      .style("border-radius", "5px")
      .style("font-family", "Open Sans Regular")

      .style("padding", "5px");

    const bars = this.mainGroup
      .selectAll<SVGRectElement, unknown>(".bar")
      .data(data);

    bars.exit().remove();

    const barEnters = bars
      .enter()
      .append("rect")
      .attr("class", "bar")
      .style(
        "fill",
        function (this: BarChart, d: Action) {
          return this.colors[this.actionToNumber[d.name] % this.colors.length];
        }.bind(this)
      );

    barEnters
      .merge(bars)
      .transition()
      .duration(200)
      .attr("x", 0)
      .attr("height", this.yScale.bandwidth())
      .attr(
        "y",
        function (this: BarChart, d: Action, index: number) {
          return (
            "" +
            (this.withNames
              ? this.yScale(store.state.Timestep.actionMeanings[index])
              : this.yScale(d.name))
          );
        }.bind(this)
      )
      .attr(
        "width",
        function (this: BarChart, d: Action) {
          return this.xScale(d.value);
        }.bind(this)
      );

    barEnters
      .on("mouseover", function (event, d: Action) {
        tooltip.style("opacity", 1);
        d3.select(this).style("stroke", "black");
        tooltip
          .html("" + d3.format(".2f")(d.value))
          .style("left", event.pageX + "px")
          .style("top", event.pageY + "px");
      })
      .on("mousemove", function () {
        bars
          .style("left", d3.pointer(this)[0] + 70 + "px")
          .style("top", d3.pointer(this)[1] + "px");
      })
      .on("mouseleave", function () {
        tooltip.style("opacity", 0);
        d3.select(this).style("stroke", "none");
      });
    if (!this.yAxisGroup || !this.xAxisGroup) {
      this.xAxisGroup = this.mainGroup
        .append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${this.height})`);

      this.yAxisGroup = this.mainGroup.append("g").attr("class", "y axis");
    }

    this.xAxisGroup
      .selectAll("text")
      .style("font-family", "Open Sans Regular")

      .attr("transform", "rotate(45)")
      .attr("x", 20);

    this.xAxisGroup.call(this.xAxis.ticks(5));
    this.yAxisGroup.call(this.yAxis);
  }

  updateData(newstepData: StepActionMap): void {
    this.stepData = newstepData;
    if (Object.keys(this.stepData).length == 0) return;
  }
}
