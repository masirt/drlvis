import * as d3 from "d3";
import { StepValueMap } from "./types";
import { NumberValue, transition } from "d3";
import { getColorPalette } from "./colorpalette";

export class DynamicBarChart {
  stepData: StepValueMap;
  margin = { top: 40, right: 20, bottom: 50, left: 55 };
  width = 380;
  height = 200;
  svg: d3.Selection<SVGSVGElement, unknown, HTMLElement | null, undefined>;
  mainGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xScale: d3.ScaleBand<string>;
  yScale: d3.ScaleLinear<number, number>;
  colors: string[];
  xAxisGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  yAxisGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xAxis: d3.Axis<string>;
  yAxis: d3.Axis<NumberValue>;
  lineDrawn = false;

  constructor(
    stepData: StepValueMap,
    domElementId: string,
    title: string,
    width: number
  ) {
    this.stepData = stepData;
    if (Object.keys(this.stepData).length == 0) return;
    this.width = width;
    this.xScale = d3 //TODO update any time you draw as its dynamic
      .scaleBand()
      .domain(Object.keys(this.stepData))
      .range([0, this.width]);

    const min = d3.min(Object.values(this.stepData), (d) => d[0]);
    this.yScale = d3
      .scaleLinear()
      .domain([
        min >= 0 ? 0 : min,
        d3.max(Object.values(this.stepData), (d) => d[0]),
      ])
      .range([this.height, 0]);

    this.colors = getColorPalette();

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

    this.mainGroup
      .append("text")
      .attr(
        "transform",
        "translate(" +
          (this.width - this.margin.left - this.margin.right) / 2 +
          " ," +
          (this.height + this.margin.bottom / 2 + 5) +
          ")"
      )
      .text("Timestep")
      .style("font-family", "Open Sans Regular")
      .attr("font-size", "12px");
  }

  setWidth(width: number) {
    if (Object.keys(this.stepData).length == 0) return;
    this.width = width;
    this.svg.attr("width", this.width + this.margin.left + this.margin.right);
  }

  drawPlot(stepCount: number): void {
    if (Object.keys(this.stepData).length == 0) return;
    if (!this.svg) return;
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("id", "tooltip")
      .attr("style", "position: absolute; opacity:0;")
      .style("background-color", "white")
      .style("font-family", "Open Sans Regular")

      .style("border", "solid")
      .style("border-width", "2px")
      .style("border-radius", "5px")
      .style("padding", "5px");
    const data: [string, number[]][] = Object.entries(this.stepData);

    this.xScale = d3
      .scaleBand()
      .domain(Object.keys(this.stepData))
      .range([0, this.width]);

    const min = d3.min(Object.values(this.stepData), (d) => d[0]);
    this.yScale = d3
      .scaleLinear()
      .domain([
        min >= 0 ? 0 : min,
        d3.max(Object.values(this.stepData), (d) => d[0]),
      ])
      .range([this.height, 0]);
    const length = Object.keys(this.stepData).length;

    this.xAxis = d3.axisBottom(this.xScale).tickValues(
      this.xScale.domain().filter(function (d, i) {
        return !(i % Math.round(length / 5));
      })
    );

    if (!this.yAxisGroup || !this.xAxisGroup) {
      this.xAxisGroup = this.mainGroup
        .append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${this.height})`);

      this.yAxisGroup = this.mainGroup.append("g").attr("class", "y axis");
    }

    this.yAxisGroup.call(this.yAxis);
    this.xAxisGroup.call(this.xAxis);
    this.drawTrendLine(data);

    const rect = this.mainGroup
      .selectAll<SVGRectElement, unknown>(".rect")
      .data(data);
    rect.exit().remove();

    const rectEnters = rect.enter().append("rect");

    rectEnters.attr("class", "rect");

    rectEnters
      .merge(rect)
      // .transition()

      // .duration(2000)
      // .ease(d3.easeCubic)
      .style(
        "fill",
        function (this: DynamicBarChart, d: [string, number[]]) {
          if ("" + stepCount == d[0]) return this.colors[0];
          return "none";
        }.bind(this)
      )
      .attr(
        "x",
        function (this: DynamicBarChart, d: [string, number[]]) {
          if ("" + stepCount == d[0]) {
            return this.xScale(d[0])!;
          }
          return this.xScale("" + 0)!;
        }.bind(this)
      )
      .attr(
        "height",
        function (this: DynamicBarChart, d: [string, number[]]) {
          if (d[1][0] == 0 && this.yScale.domain()[1] != 0) {
            return this.height - this.yScale(d[1][0]) + 5;
          }
          return this.height - this.yScale(d[1][0]);
        }.bind(this)
      )
      .attr(
        "y",
        function (this: DynamicBarChart, d: [string, number[]]) {
          if (d[1][0] == 0 && this.yScale.domain()[1] != 0) {
            return this.yScale(d[1][0]) - 5;
          }
          return this.yScale(d[1][0]);
        }.bind(this)
      )
      .attr("width", this.xScale.bandwidth());

    rectEnters
      .on("mouseover", function (event, d: [string, number[]]) {
        tooltip.style("opacity", 1);
        d3.select(this).style("stroke", "black");
        d3.select(this).attr(
          "width",
          Number.parseInt(d3.select(this).attr("width")) * 3
        );
        d3.select(this).attr(
          "x",
          Number.parseInt(d3.select(this).attr("x")) -
            Number.parseInt(d3.select(this).attr("width")) / 2
        );
        tooltip
          .html(
            `Value: ${d3.format(".2f")(d[1][0])} \n 
                 Timestep: ${d[0]}`
          )
          .style("left", event.pageX + "px")
          .style("top", event.pageY + "px");
      })
      .on("mousemove", function () {
        rect
          .style("left", d3.pointer(this)[0] + 70 + "px")
          .style("top", d3.pointer(this)[1] + "px");
      })
      .on("mouseleave", function () {
        tooltip.style("opacity", 0);
        d3.select(this).style("stroke", "none");
        d3.select(this).attr(
          "x",
          Number.parseInt(d3.select(this).attr("x")) +
            Number.parseInt(d3.select(this).attr("width")) / 2
        );
        d3.select(this).attr(
          "width",
          Number.parseInt(d3.select(this).attr("width")) / 3
        );
      });
    if (!this.yAxisGroup || !this.xAxisGroup) {
      this.xAxisGroup = this.mainGroup
        .append("g")
        .attr("class", "x axis")
        .attr("transform", `translate(0,${this.height})`);
    }
  }
  updateData(newstepData: StepValueMap, timestepnumber: number): void {
    this.stepData = newstepData;
    if (Object.keys(this.stepData).length == 0) return;
    this.drawPlot(timestepnumber);
  }

  drawTrendLine(data: [string, number[]][]) {
    if (Object.keys(this.stepData).length == 0) return;
    const line = d3
      .line()
      .x(
        function (this: DynamicBarChart, d: [number, number]) {
          return this.xScale("" + d[0])!;
        }.bind(this)
      )
      .y(
        function (this: DynamicBarChart, d: [number, number]) {
          return this.yScale(d[1]);
        }.bind(this)
      )
      .curve(d3.curveBasis);

    const linedata: any[] | string | null = this.convertToLine(data);

    if (this.lineDrawn) {
      this.mainGroup.select(".line").attr("d", line(linedata)!);
    } else {
      this.mainGroup
        .append("path")
        .datum(linedata)
        .attr("class", "line")
        .attr("stroke", "" + this.colors[1])
        .attr("stroke-width", 3)
        .attr("fill", "none")
        .attr("d", line(linedata)!);

      this.lineDrawn = true;
    }
  }
  convertToLine(data: [string, number[]][]) {
    const startData = data;
    const lineData = new Array(startData.length);
    startData.forEach((elem: any, index) => {
      lineData[index] = [elem[0], elem[1][1]];
    });
    return lineData;
  }
}
