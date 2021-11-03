import Vue from "vue";
import Vuex from "vuex";

import General from "./module/general";
import Timestep from "./module/timestep";
import Confidence from "./module/confidence";
import Episode from "./module/episode";

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    General,
    Timestep,
    Confidence,
    Episode,
  },
});

export default store;
