import * as d3 from "d3";
import { WeightMatrix } from "./types";
import store from "../store/index";
import { bin, NumberValue, text } from "d3";
import { getColorPalette } from "./colorpalette";

export class Histogram {
  margin = { top: 40, right: 20, bottom: 50, left: 65 };
  width = 380;
  height = 240;
  svg: d3.Selection<SVGSVGElement, unknown, HTMLElement | null, undefined>;
  currentData: number[];
  mainGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xScale: d3.ScaleLinear<number, number>;
  yScale: d3.ScaleBand<string>;
  xAxis: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  yAxis: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  bins: d3.HistogramGeneratorNumber<number, number>;
  colors: string[];
  episodeWeightMatrix: WeightMatrix;
  binsSum: number;
  domElementId: string;

  constructor(
    episodeWeightMatrix: WeightMatrix,
    domElementId: string,
    title: string,
    width: number
  ) {
    this.episodeWeightMatrix = episodeWeightMatrix;
    if (Object.keys(this.episodeWeightMatrix).length <= 0) return;
    this.width = width;
    this.domElementId = domElementId;

    this.currentData = [];
    this.colors = getColorPalette();
    episodeWeightMatrix[0].forEach((elem) => {
      this.currentData.push(Object.values(elem)[0] as number);
    });
    this.binsSum = 1;

    this.svg = d3
      .select(`#${domElementId}`)
      .append("svg")
      .attr("width", this.width + this.margin.left + this.margin.right)
      .attr("height", this.height + this.margin.top + this.margin.bottom + 10);

    this.mainGroup = this.svg
      .append("g")
      .attr("transform", `translate(${this.margin.left}, ${this.margin.top})`);

    this.mainGroup
      .append("text")
      .attr(
        "transform",
        `translate(${(this.width + this.margin.right) / 2}, ${
          this.height + this.margin.bottom
        })`
      )
      .attr("class", "x-axis-text")
      .text("#Weights in Bucket")
      .style("font-family", "Open Sans Regular")
      .style("text-anchor", "middle")
      .attr("font-size", "12px");

    this.bins = d3.bin();

    const bins = this.bins(this.currentData);

    this.xScale = d3
      .scaleLinear()
      .range([0, this.width])
      .domain([
        0,
        d3.max(bins, function (d) {
          return d.length;
        })!,
      ]);

    this.xAxis = this.mainGroup
      .append("g")
      .attr("class", "x axis")
      .attr("transform", `translate(0,${this.height})`)
      .call(d3.axisBottom(this.xScale).tickValues([]));

    this.yScale = d3
      .scaleBand()
      .domain(
        d3.map(bins, function (d) {
          return `${d["x0"]} - ${d["x1"]}`;
        })
      )
      .range([0, this.height])
      .paddingInner(0.25)
      .paddingOuter(0.2);

    this.svg
      .append("text")
      .attr("x", 0)
      .attr("y", this.margin.top / 2)
      .attr("text-anchor", "left")
      .style("font-size", "14px")
      .style("font-family", "Open Sans Regular")

      .text(`${title}`);

    this.drawHistogram();
  }

  update(
    episodeWeightMatrix: WeightMatrix,
    currentAnimationFrame: number
  ): void {
    if (episodeWeightMatrix[0] !== undefined) {
      this.episodeWeightMatrix = episodeWeightMatrix;
    }
    if (!this.episodeWeightMatrix[currentAnimationFrame]) {
      return;
    }
    this.currentData = [];

    this.episodeWeightMatrix[currentAnimationFrame].forEach((elem) => {
      this.currentData.push(Object.values(elem)[0] as number);
    });
    this.drawHistogram();
  }

  setWidth(width: number) {
    this.width = width;
    this.svg.attr("width", this.width + this.margin.left + this.margin.right);
  }

  drawHistogram(): void {
    if (Object.keys(this.episodeWeightMatrix).length <= 0) {
      return;
    }

    const binnedData = this.bins(this.currentData);
    let domain: NumberValue[] = [];

    if (store.state.Timestep.scaleMinMax) {
      domain = [0, 1];
      this.binsSum = d3.sum(binnedData, function (d) {
        return d.length;
      });
    } else {
      this.binsSum = 1;
      domain = [
        0,
        d3.max(binnedData, function (d) {
          return d.length;
        })!,
      ];
    }
    this.xScale.domain(domain);
    this.xScale.range([0, this.width]);

    this.yScale.domain(
      d3.map(binnedData, function (d) {
        return `${d["x0"]} - ${d["x1"]}`;
      })
    );

    const rects = this.mainGroup
      .selectAll<SVGRectElement, unknown>(".rect")
      .data(binnedData);
    rects.exit().remove();

    const rectEnters = rects
      .enter()
      .append("rect")
      .attr("class", "rect")
      .style("fill", "" + this.colors[0]);

    rectEnters
      .merge(rects)
      .transition()
      .duration(200)
      .attr("x", 0)
      .attr(
        "y",
        function (this: Histogram, d: d3.Bin<number, number>) {
          return "" + this.yScale("" + d["x0"] + " - " + d["x1"]);
        }.bind(this)
      )
      .attr(
        "width",
        function (this: Histogram, d: number[]) {
          return this.xScale(d.length / this.binsSum);
        }.bind(this)
      )
      .attr("height", this.yScale.bandwidth());

    if (!this.yAxis) {
      this.yAxis = this.mainGroup
        .append("g")
        .attr("class", "y axis")

        .call(d3.axisLeft(this.yScale).ticks(5));
    }
    this.yAxis.call(d3.axisLeft(this.yScale).ticks(5));
    this.xAxis.call(d3.axisBottom(this.xScale));
    this.xAxis
      .selectAll("text")
      .attr("transform", "rotate(90)")
      .style("font-family", "Open Sans Regular")

      .attr("x", 27)
      .attr("y", -2);

    const tooltip = d3
      .select("body")
      .append("div")
      .attr("id", "tooltip")
      .attr("style", "position: absolute; opacity:0;")
      .style("font-family", "Open Sans Regular")

      .style("background-color", "white")
      .style("border", "solid")
      .style("border-width", "2px")
      .style("border-radius", "5px")
      .style("padding", "5px");

    rectEnters
      .on(
        "mouseover",
        function (this: Histogram, event: any, d: d3.Bin<number, number>) {
          tooltip.style("opacity", 1);
          //d3.select(this).style("stroke", "black");
          tooltip
            .html("" + d3.format(".2f")(d.length / this.binsSum))
            .style("left", event.pageX + "px")
            .style("top", event.pageY + "px");
        }.bind(this)
      )
      .on("mousemove", function () {
        rects
          .style("left", d3.pointer(this)[0] + 70 + "px")
          .style("top", d3.pointer(this)[1] + "px");
        d3.select(this).style("stroke", "black");
      })
      .on("mouseleave", function () {
        tooltip.style("opacity", 0);
        d3.select(this).style("stroke", "none");
      });
  }
}
