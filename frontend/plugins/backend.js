import axios from "axios"
import accounts from "@/api/accounts"
import arbiters from "@/api/arbiters"
import national_elo_archive from "@/api/national_elo_archive"
import club from "@/api/club"
import fide from "@/api/fide"
import filestore from "@/api/filestore"
import interclub from "@/api/interclub"
import member from "@/api/member"
import players_fide from "@/api/players_fide"
import test from "@/api/test"

axios.defaults.withCredentials = true

const error_messages = {
  401: "Authentication required",
  403: "Permission denied",
  404: "Not found",
  500: "General server error",
  503: "Could not connect to database server",
  600: "Connection issue: server unreachable",
  700: "You triggered a bug.  Please inform the webmaster.",
  Forbidden: "Permission denied",
  WrongUsernamePasswordCombination:
    "Wrong combination of username and password",
}

axios.interceptors.response.use(
  (response) => {
    return Promise.resolve({
      data: response.data,
      headers: response.headers,
    })
  },
  (error) => {
    if (error.response) {
      // `detail` is the FastAPI convention (HTTPException(detail=...)), used
      // by every proxied-to-FastAPI feature. A Node-backed endpoint returns
      // {message: "..."} instead, so that is the fallback; without it such an
      // error resolves to `undefined` and the form can only show a generic
      // "...failed" string. error_messages has no 400 entry either, so the
      // final fallback covers that gap too instead of leaving `message`
      // undefined.
      const detail = error.response.data.detail
      const backendMessage = error.response.data.message
      console.info(
        "backend Axios",
        error.response.status,
        detail || backendMessage,
        error.request
      )
      return Promise.reject({
        code: error.response.status,
        // Stable, language-independent machine code for callers that need
        // to branch on a specific failure reason without string-matching
        // English backend text; undefined for every response that doesn't
        // set one.
        errorCode: error.response.data.code,
        headers: error.response.headers,
        message:
          detail ||
          backendMessage ||
          error_messages[error.response.status] ||
          `Request failed (${error.response.status})`,
      })
    }
    if (error.request) {
      console.warn("Axios", "No response received", error.request)
      return Promise.reject({
        code: 600,
        message: error_messages[600],
      })
    }
    console.warn("Axios", "No request sent", error.message)
    return Promise.reject({
      code: 700,
      message: error_messages[700],
    })
  }
)

const factories = {
  accounts,
  arbiters,
  national_elo_archive,
  club,
  fide,
  filestore,
  interclub,
  member,
  players_fide,
  test,
}

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  axios.defaults.baseURL = runtimeConfig.public.apiUrl
  
  return {
    provide: {
      backend: async function (fact, method, options) {
        const f = factories[fact][method]
        if (!f) {
          console.log("$backend method not existing", fact, method)
        }
        console.log("calling $backend", fact, method, options)
        // console.log("with baseURL", axios.defaults.baseURL)
        return await f(options)
      },
    },
  }
})
