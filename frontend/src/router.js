import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import HowTo from './views/HowTo.vue'
import Map from './views/Map.vue'
import Edit from './views/Edit.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/map',
      name: 'map',
      component: Map
    },
    {
      path: '/edit',
      name: 'edit',
      component: Edit
    },
    {
      path: '/howto',
      name: 'howto',
      component: HowTo
    }
  ]
})
