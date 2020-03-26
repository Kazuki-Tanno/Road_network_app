import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    Network: {node:[], edge:[]}
  },
  mutations: {
    UpdateNetwork(state, payload){
      state.Network = payload
    }
  },
  actions: {
    UpdateNetwork(context, payload){
      context.commit('UpdateNetwork', payload);
    }
  },
  modules: {
  }
})
