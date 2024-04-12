import axios from "axios"
import accounts from "@/api/accounts"
import club from "@/api/club"
import content from "@/api/content"
import file from "@/api/file"
import interclub from "@/api/interclub"
import member from "@/api/member"

axios.defaults.withCredentials = true

const error_messages = {
  401: "Authentication required",
  403: "Permission denied",
  404: "Not found",
  422: "Request validation error",
  500: "General server error",
  503: "Could not connect to database server",
  600: "Connectiom issue: server unreachable",
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
      const errdata = error.response.data
      const detail = errdata?.detail
      console.error("backend error", error.response.status, detail)
      const message = error_messages[detail] ? error_messages[detail] : error_messages[error.response.status]
      console.error('message', message)
      return Promise.reject({
        code: error.response.status,
        headers: error.response.headers,
        message: message,
      });

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
  club,
  content,
  file,
  interclub,
  member,
}

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  axios.defaults.baseURL = runtimeConfig.public.apiurl
  return {
    provide: {
      backend: async function (fact, method, options) {
        const f = factories[fact][method]
        if (!f) {
          console.log("method not existing", fact, method)
        }
        let now = new Date()
        let reply = await f(options);
        console.warn("backend call", method, "replied in ms:", new Date() - now)
        return reply
      },
    },
  }
})
