<template>
  <div>
    <h2>{{ heading }}</h2>
  </div>
</template>

<script lang="ts">
import { Vue, Prop, Component } from "vue-property-decorator";

@Component
export default class SubHeading extends Vue {
  name: "Subheading";

  @Prop() heading: string;
}
</script>

<style>
h2 {
  color: black;
  text-align: left;
  margin-top: 10px;
  min-width: 200px;
  border-radius: 5px;
  width: 20%;
  font-family: "Open Sans Regular";
}
</style>
