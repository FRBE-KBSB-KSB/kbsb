import Vue from 'vue'
import VueRouter from 'vue-router'

import RouteNotFound from './RouteNotFound.vue'

Vue.use(VueRouter);

const router = new VueRouter({
  routes: [
    {path: '/page/_notfound', component: RouteNotFound},
    {path: '*', redirect: '/page/_notfound'},
  ],
  mode: 'history'
});

//  dynamic adding of routes possible

import CmsSimplePage from './CmsSimplePage.vue'
import LandingPage from './LandingPage.vue'
import MultiLocalePage from './MultiLocalePage.vue'

let dynroutes = {
  CmsSimplePage: CmsSimplePage,
  LandingPage: LandingPage,
  MultiLocalePage: MultiLocalePage,
}


function processRoutes(rts) {
  // cycle through routes from api and construct routing table 
  let rtable = [];
  rts.forEach(function(rt) {
    rtable.push({
      component: (rt.component in dynroutes) ? dynroutes[rt.component] : RouteNotFound,
      path: '/page/' + rt.slug + '/:locale'
    })
  })
  console.log('rtable', rtable)
  return rtable
}


export {router, processRoutes};