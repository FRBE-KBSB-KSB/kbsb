import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _031757e9 = () => interopDefault(import('../pages/board.vue' /* webpackChunkName: "pages/board" */))
const _32b2bbd5 = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))
const _16068a50 = () => interopDefault(import('../pages/interclub-2021-22.vue' /* webpackChunkName: "pages/interclub-2021-22" */))
const _714ce710 = () => interopDefault(import('../pages/partners.vue' /* webpackChunkName: "pages/partners" */))
const _e6041ea4 = () => interopDefault(import('../pages/statutes.vue' /* webpackChunkName: "pages/statutes" */))

const emptyFn = () => {}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: '/',
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/board",
    component: _031757e9,
    name: "board"
  }, {
    path: "/de",
    component: _32b2bbd5,
    name: "index___de"
  }, {
    path: "/en",
    component: _32b2bbd5,
    name: "index___en"
  }, {
    path: "/fr",
    component: _32b2bbd5,
    name: "index___fr"
  }, {
    path: "/interclub-2021-22",
    component: _16068a50,
    name: "interclub-2021-22"
  }, {
    path: "/nl",
    component: _32b2bbd5,
    name: "index___nl"
  }, {
    path: "/partners",
    component: _714ce710,
    name: "partners"
  }, {
    path: "/statutes",
    component: _e6041ea4,
    name: "statutes"
  }, {
    path: "/de/board",
    component: _031757e9,
    name: "board___de"
  }, {
    path: "/de/interclub-2021-22",
    component: _16068a50,
    name: "interclub-2021-22___de"
  }, {
    path: "/de/partners",
    component: _714ce710,
    name: "partners___de"
  }, {
    path: "/de/statutes",
    component: _e6041ea4,
    name: "statutes___de"
  }, {
    path: "/en/board",
    component: _031757e9,
    name: "board___en"
  }, {
    path: "/en/interclub-2021-22",
    component: _16068a50,
    name: "interclub-2021-22___en"
  }, {
    path: "/en/partners",
    component: _714ce710,
    name: "partners___en"
  }, {
    path: "/en/statutes",
    component: _e6041ea4,
    name: "statutes___en"
  }, {
    path: "/fr/board",
    component: _031757e9,
    name: "board___fr"
  }, {
    path: "/fr/interclub-2021-22",
    component: _16068a50,
    name: "interclub-2021-22___fr"
  }, {
    path: "/fr/partners",
    component: _714ce710,
    name: "partners___fr"
  }, {
    path: "/fr/statutes",
    component: _e6041ea4,
    name: "statutes___fr"
  }, {
    path: "/nl/board",
    component: _031757e9,
    name: "board___nl"
  }, {
    path: "/nl/interclub-2021-22",
    component: _16068a50,
    name: "interclub-2021-22___nl"
  }, {
    path: "/nl/partners",
    component: _714ce710,
    name: "partners___nl"
  }, {
    path: "/nl/statutes",
    component: _e6041ea4,
    name: "statutes___nl"
  }, {
    path: "/",
    component: _32b2bbd5,
    name: "index"
  }],

  fallback: false
}

export function createRouter (ssrContext, config) {
  const base = (config._app && config._app.basePath) || routerOptions.base
  const router = new Router({ ...routerOptions, base  })

  // TODO: remove in Nuxt 3
  const originalPush = router.push
  router.push = function push (location, onComplete = emptyFn, onAbort) {
    return originalPush.call(this, location, onComplete, onAbort)
  }

  const resolve = router.resolve.bind(router)
  router.resolve = (to, current, append) => {
    if (typeof to === 'string') {
      to = normalizeURL(to)
    }
    return resolve(to, current, append)
  }

  return router
}
