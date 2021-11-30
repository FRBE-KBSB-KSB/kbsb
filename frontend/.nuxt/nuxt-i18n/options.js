

export const Constants = {
  COMPONENT_OPTIONS_KEY: "nuxtI18n",
  STRATEGIES: {"PREFIX":"prefix","PREFIX_EXCEPT_DEFAULT":"prefix_except_default","PREFIX_AND_DEFAULT":"prefix_and_default","NO_PREFIX":"no_prefix"},
  REDIRECT_ON_OPTIONS: {"ALL":"all","ROOT":"root","NO_PREFIX":"no prefix"},
}
export const nuxtOptions = {
  isUniversalMode: true,
  trailingSlash: undefined,
}
export const options = {
  vueI18n: {"silentTranslationWarn":false,"silentFallbackWarn":true},
  vueI18nLoader: false,
  locales: [{"code":"nl","file":"nl.js"},{"code":"fr","file":"fr.js"},{"code":"de","file":"de.js"},{"code":"en","file":"en.js"}],
  defaultLocale: "nl",
  defaultDirection: "ltr",
  routesNameSeparator: "___",
  defaultLocaleRouteNameSuffix: "default",
  sortRoutes: true,
  strategy: "prefix",
  lazy: true,
  langDir: "/home/ruben/develop/cms/kbsb/frontend/lang",
  rootRedirect: null,
  detectBrowserLanguage: {"alwaysRedirect":false,"cookieCrossOrigin":false,"cookieDomain":null,"cookieKey":"i18n_redirected","cookieSecure":false,"fallbackLocale":"","redirectOn":"root","useCookie":true},
  differentDomains: false,
  baseUrl: "",
  vuex: {"moduleName":"i18n","syncRouteParams":true},
  parsePages: true,
  pages: {},
  skipSettingLocaleOnNavigate: false,
  onBeforeLanguageSwitch: () => {},
  onLanguageSwitched: () => null,
  normalizedLocales: [{"code":"nl","file":"nl.js"},{"code":"fr","file":"fr.js"},{"code":"de","file":"de.js"},{"code":"en","file":"en.js"}],
  localeCodes: ["nl","fr","de","en"],
  additionalMessages: [],
}

export const localeMessages = {
  'nl.js': () => import('../../lang/nl.js' /* webpackChunkName: "lang-nl.js" */),
  'fr.js': () => import('../../lang/fr.js' /* webpackChunkName: "lang-fr.js" */),
  'de.js': () => import('../../lang/de.js' /* webpackChunkName: "lang-de.js" */),
  'en.js': () => import('../../lang/en.js' /* webpackChunkName: "lang-en.js" */),
}
