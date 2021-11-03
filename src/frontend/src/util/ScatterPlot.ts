import * as d3 from "d3";
import { EpisodeValueMap } from "./types";
import store from "../store/index";
import { namespace, State } from "vuex-class";
import { AxisScale } from "d3";
import Timestep from "@/store/module/timestep";
import { getColorPalette } from "./colorpalette";

const general = namespace("General");

export class ScatterPlot {
  margin = { top: 60, right: 50, bottom: 60, left: 50 };
  width = 550; // Use the window's width
  height = 200; // Use the window's height
  episodeValueMap: EpisodeValueMap;
  svg: d3.Selection<SVGSVGElement, unknown, HTMLElement | null, undefined>;
  mainGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xScale: d3.ScaleLinear<number, number>;
  yScale: d3.ScaleLinear<number, number>;
  colors: string[];
  domElementId: string;
  yAxis: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xAxis: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  lineDrawn = false;

  constructor(
    episodeValueMap: EpisodeValueMap,
    domElementId: string,
    title: string,
    width: number
  ) {
    this.episodeValueMap = episodeValueMap;
    this.domElementId = domElementId;
    this.width = width;

    if (Object.keys(this.episodeValueMap).length <= 0) return;

    this.colors = getColorPalette();

    this.xScale = d3
      .scaleLinear()
      .domain([0, Object.keys(this.episodeValueMap).length])
      .range([0, this.width]);

    this.yScale = d3
      .scaleLinear()
      .domain([0, d3.max(Object.values(this.episodeValueMap), (d) => d[0])])
      .range([this.height, 0]);

    this.svg = d3
      .select(`#${domElementId}`)
      .append("svg")

      .attr("width", this.width + this.margin.left + this.margin.right)
      .attr("height", this.height + this.margin.top + this.margin.bottom);

    this.mainGroup = this.svg
      .append("g")
      .attr(
        "transform",
        "translate(" + this.margin.left + "," + this.margin.top + ")"
      );

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
      .text("Episode Count")
      .style("font-family", "Open Sans Regular")

      .attr("font-size", "12px");

    this.mainGroup
      .append("text")
      .attr("y", 0 - this.margin.left / 2 - 10)
      .attr("x", 0 - (this.height + this.margin.top + this.margin.bottom) / 2)
      .text(title)
      .style("font-family", "Open Sans Regular")

      .attr("transform", "rotate(-90)")
      .attr("font-size", "14px");

    this.xAxis = this.mainGroup
      .append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + this.height + ")")
      .call(d3.axisBottom(this.xScale));

    this.yAxis = this.mainGroup
      .append("g")
      .attr("class", "y axis")
      .call(d3.axisLeft(this.yScale).ticks(5));

    this.mainGroup
      .append("text")
      .attr("x", 0)
      .attr("y", 0 - this.margin.top / 2)
      .attr("text-anchor", "left")
      .style("font-size", "16px")
      .style("font-family", "Open Sans Regular")

      .text(`${title}`);
  }
  setWidth(width: number) {
    this.width = width;
    this.svg.attr("width", this.width + this.margin.left + this.margin.right);
  }

  drawScatterPlot(selectedEpisode: string, hoveredEpisode: string) {
    if (Object.keys(this.episodeValueMap).length <= 0) return;

    this.xScale = d3
      .scaleLinear()
      .domain([0, Object.keys(this.episodeValueMap).length])
      .range([0, this.width]);

    this.yScale = d3
      .scaleLinear()
      .domain([0, d3.max(Object.values(this.episodeValueMap), (d) => d[0])])
      .range([this.height, 0]);

    this.xAxis.call(d3.axisBottom(this.xScale));
    this.yAxis.call(d3.axisLeft(this.yScale).ticks(5));

    d3.selectAll(".path").remove();

    const dots = this.mainGroup
      .selectAll<SVGCircleElement, unknown>(".dot")
      .data(Object.entries(this.episodeValueMap));

    const dotEnters = dots.enter().append("circle");

    dotEnters
      .merge(dots)
      .attr("class", "dot")
      .attr(
        "stroke",
        function (this: ScatterPlot, d: [string, number[]]) {
          if (d[0] === selectedEpisode) {
            return this.colors[2];
          }
          return "" + this.colors[0];
        }.bind(this)
      )
      .attr(
        "fill",
        function (this: ScatterPlot, d: [string, number[]]) {
          if (d[0] === selectedEpisode) {
            return this.colors[2];
          }
          return "" + this.colors[0];
        }.bind(this)
      )
      .attr(
        "cx",
        function (this: ScatterPlot, d: [string, number[]]) {
          return this.xScale(Number.parseFloat(d[0]));
        }.bind(this)
      )
      .attr(
        "cy",
        function (this: ScatterPlot, d: [string, number[]]) {
          return this.yScale(d[1][0]);
        }.bind(this)
      )
      .attr(
        "r",
        function (this: ScatterPlot, d: [string, number[]]) {
          if (d[0] === hoveredEpisode) {
            return 12;
          }
          return 4;
        }.bind(this)
      );
    this.drawTrendLine();

    dotEnters
      .on("mouseenter", function (actual, d: [string, number[]]) {
        store.state.General.hoveredEpisode = Number.parseInt(d[0]);
      })
      .on("mouseleave", function (event, d: [string, number[]]) {
        d3.select(this).style("stroke", "none").style("opacity", 0.8);
        const tooltip = d3
          .select("body")
          .append("div")
          .attr("id", "tooltipscatter")
          .attr("style", "position: absolute")
          .style("opacity", 0)
          .style("background-color", "white")
          .style("border", "solid")
          .style("border-width", "2px")
          .style("border-radius", "5px")
          .style("font-family", "Open Sans Regular")

          .style("padding", "5px");
        tooltip.style("opacity", 0);
        tooltip.style("opacity", 0);
        d3.selectAll("#tooltipscatter").remove();
        d3.select(this).style("stroke", "none");
        store.state.General.hoveredEpisode = -1;
      })
      .on("click", function (event: MouseEvent, d: [string, number]) {
        store.state.General.selectedEpisode = Number.parseInt(d[0]);
      });

    dotEnters
      .on("mouseover", function (event, d: [string, number[]]) {
        const tooltip = d3
          .select("body")
          .append("div")
          .attr("id", "tooltipscatter")
          .attr("style", "position: absolute")
          .style("opacity", 0)
          .style("background-color", "white")
          .style("border", "solid")
          .style("border-width", "2px")
          .style("border-radius", "5px")
          .style("padding", "5px");
        tooltip.style("opacity", 1);
        d3.select(this).style("stroke", "black");
        tooltip
          .html("" + d3.format(".2f")(d[1][0]))
          .style("left", event.pageX + "px")
          .style("top", event.pageY + "px");
      })
      .on("mousemove", function () {
        dots
          .style("left", d3.pointer(this)[0] + 70 + "px")
          .style("top", d3.pointer(this)[1] + "px");
      });

    dots.exit().remove();
  }

  drawTrendLine() {
    const line = d3
      .line()
      .x(
        function (this: ScatterPlot, d: [number, number]) {
          return this.xScale(d[0]);
        }.bind(this)
      )
      .y(
        function (this: ScatterPlot, d: [number, number]) {
          return this.yScale(d[1]);
        }.bind(this)
      )
      .curve(d3.curveBasis);

    const linedata: any[] | string | null = this.convertToLine();

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
  convertToLine() {
    const startData = Object.entries(this.episodeValueMap);
    const lineData = new Array(startData.length);
    startData.forEach((elem, index) => {
      lineData[index] = [Number.parseFloat(elem[0]), elem[1][1]];
    });
    return lineData;
  }
}
