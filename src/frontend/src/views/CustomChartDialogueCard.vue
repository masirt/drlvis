<template>
  <v-card>
    <v-card-title>Select logging tag </v-card-title>
    <v-divider></v-divider>

    <v-card-text style="height: 300px">
      <v-text-field
        label="Chart Title"
        v-model="customChartTitle"
      ></v-text-field>
      <v-radio-group v-model="selectedLogTag" column label="Logged Tag">
        <v-radio
          v-for="logTag in logTagList"
          :key="logTag"
          :label="logTag"
          :value="logTag"
        />
      </v-radio-group>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-btn color="#818a89" text @click="dialog = false"> Close </v-btn>
      <v-btn color="#818a89" text @click="addNewCustomData"> Save </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class CustomChartDialogueCard extends Vue {
  name: "CustomChartDialogue";

  @Prop()
  public customChartTitle: string;

  @Prop()
  public selectedLogTag = "";

  @Prop()
  public logTagList: Array<string>;

  @Prop()
  public dialog: boolean;

  @Prop()
  public addNewCustomData: (customData: any) => void;
}
</script>
