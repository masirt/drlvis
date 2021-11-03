import * as d3 from "d3";
import { ExperimentalMap } from "./types";
import store from "../store/index";
import { NumberValue } from "d3";
import { getColorPalette } from "./colorpalette";
import { BASE_URL } from "./baseurl";

export class ExperimentalScatterplot {
  margin = { top: 50, right: 20, bottom: 100, left: 20 };
  width = 900; // Use the window's width
  height = 600; // Use the window's height
  experimentalMap: ExperimentalMap;
  svg: d3.Selection<SVGSVGElement, unknown, HTMLElement | null, undefined>;
  mainGroup: d3.Selection<SVGGElement, unknown, HTMLElement | null, undefined>;
  xScale: d3.ScaleLinear<number, number>;
  yScale: d3.ScaleLinear<number, number>;
  colors: string[];
  domElementId: string;
  promise: Promise<any>;

  constructor(
    experimentalMap: ExperimentalMap,
    domElementId: string,
    width: number,
    height: number
  ) {
    this.experimentalMap = experimentalMap;
    if (Object.keys(this.experimentalMap).length <= 0) return;

    if (width) this.width = width;
    if (height) this.height = height;

    this.domElementId = domElementId;
    this.colors = getColorPalette();

    this.xScale = d3
      .scaleLinear()
      .domain(
        d3.extent(experimentalMap.values, (d) => d[0]) as Iterable<number>
      )
      .range([0, this.width]);
    this.yScale = d3
      .scaleLinear()
      .domain(
        d3.extent(experimentalMap.values, (d) => d[1]) as Iterable<number>
      )
      .range([this.height, 0]);

    this.svg = d3
      .select(`#${domElementId}`)
      .append("svg")
      .attr("width", this.margin.right + this.margin.left + this.width)
      .attr("height", this.margin.top + this.margin.bottom + this.height);

    this.mainGroup = this.svg
      .append("g")
      .attr(
        "transform",
        "translate(" + this.margin.left + "," + this.margin.top + ")"
      );
  }

  setWidthandHeight(width: number, height: number) {
    if (Object.keys(this.experimentalMap).length == 0) return;
    this.width = width;
    this.height = height;
    this.svg.attr("width", this.width + this.margin.left + this.margin.right);
    this.svg.attr("height", this.height + this.margin.top + this.margin.bottom);
  }

  drawScatterPlot(experimentalMap: ExperimentalMap, episode: number): void {
    if (Object.keys(this.experimentalMap).length <= 0) return;

    this.xScale
      .domain(
        d3.extent(experimentalMap.values, (d) => d[0]) as Iterable<number>
      )
      .range([0, this.width]);
    this.yScale
      .domain(
        d3.extent(experimentalMap.values, (d) => d[1]) as Iterable<number>
      )
      .range([this.height, 0]);
    const dots = this.mainGroup
      .selectAll<SVGCircleElement, unknown>(".dot")
      .data(experimentalMap.values);

    const dotEnters = dots
      .enter()
      .append("circle")
      .attr("class", "dot")
      .attr("stroke", "white");

    dotEnters
      .merge(dots)
      .transition()
      .duration(750)
      .attr(
        "cx",
        function (this: ExperimentalScatterplot, d: number[]) {
          return this.xScale(d[0]);
        }.bind(this)
      )
      .attr(
        "cy",
        function (this: ExperimentalScatterplot, d: number[]) {
          return this.yScale(d[1]);
        }.bind(this)
      )
      .attr("r", 3)
      .style(
        "fill",
        function (this: ExperimentalScatterplot, d: number[]) {
          return this.colors[d[2] % this.colors.length];
        }.bind(this)
      )
      .attr(
        "fill-opacity",
        function (this: ExperimentalScatterplot, d: number[]) {
          return d[3];
        }.bind(this)
      )
      .attr(
        "stroke",
        function (this: ExperimentalScatterplot, d: number[]) {
          return this.colors[d[2] % this.colors.length];
        }.bind(this)
      )
      .attr("stroke-width", 1)
      .attr("id", function (d, i) {
        return i;
      });

    const this_: ExperimentalScatterplot = this;

    dotEnters

      .on("mouseenter", function (event, d: number[]) {
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

        let tooltipText = "";
        if (this_.promise) {
          this_.promise.then(Promise.reject.bind(Promise)).catch(() => {
            1;
          });
        }

        tooltipText += `Confidence: ${d3.format(".2f")(d[3])}`;
        tooltipText += `<br> Action: ${
          store.state.Timestep.actionMeanings
            ? store.state.Timestep.actionMeanings![d[2]]
            : "action " + d[2]
        }`;

        if (store.state.Confidence.isNoImageData) {
          tooltipText += "<br> State Values:";
          d.slice(4).forEach((elem, index) => {
            tooltipText +=
              `<br> state value ${index}: ` + d3.format(".2f")(elem);
          });
          tooltip.style("opacity", 1);
          tooltip
            .html(tooltipText)
            .style("left", event.pageX + "px")
            .style("top", event.pageY + "px");
          d3.select(this).attr(
            "r",
            Number.parseFloat(d3.select(this).attr("r")) * 5
          );
        } else {
          const index = Number(d3.select(this).attr("id"));

          this_.promise = this_
            .requestData(episode, index)
            .then((val) => {
              tooltipText += "<br/>";
              tooltipText +=
                "<img style=width:100% src=data:image/jpeg;base64," +
                val["confidenceFrames"][0] +
                " />";
              tooltip.style("opacity", 1);
              tooltip
                .html(tooltipText)
                .style("left", event.pageX + "px")
                .style("top", event.pageY + "px");
              d3.select(this).attr(
                "r",
                15 //Number.parseFloat(d3.select(this).attr("r")) * 5
              );
            })
            .catch(() => {
              1;
            });
        }
      })

      .on("mousemove", function () {
        dots

          .style("left", d3.pointer(this)[0] + 70 + "px")
          .style("top", d3.pointer(this)[1] + "px");
      })
      .on("mouseleave", function (d: number) {
        //tooltip.style("opacity", 0);
        d3.select(this).attr("r", 3);
        dotEnters.attr("r", 3);
        d3.selectAll("#tooltip").remove();
      });

    dots.exit().remove();
  }

  requestData(episode: number, index: number) {
    const promise = fetch(
      "" + BASE_URL + `/get-confidence-frame?user=${episode},${index}`,
      {
        method: "GET",
      }
    ).then((response) => response.json());

    return promise;
  }
}
