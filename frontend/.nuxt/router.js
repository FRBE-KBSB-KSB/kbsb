import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _32b2bbd5 = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))
const _714ce710 = () => interopDefault(import('../pages/partners.vue' /* webpackChunkName: "pages/partners" */))

const emptyFn = () => {}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: '/',
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
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
    path: "/nl",
    component: _32b2bbd5,
    name: "index___nl"
  }, {
    path: "/partners",
    component: _714ce710,
    name: "partners"
  }, {
    path: "/de/partners",
    component: _714ce710,
    name: "partners___de"
  }, {
    path: "/en/partners",
    component: _714ce710,
    name: "partners___en"
  }, {
    path: "/fr/partners",
    component: _714ce710,
    name: "partners___fr"
  }, {
    path: "/nl/partners",
    component: _714ce710,
    name: "partners___nl"
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
