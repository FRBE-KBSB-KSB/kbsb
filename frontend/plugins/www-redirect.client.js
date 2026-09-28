// The site only works on www: every API call goes to https://www.frbe-kbsb-ksb.be
// (API_URL at build time), and from the bare domain the browser refuses those
// answers (CORS) and Google refuses the admin login (origin_mismatch). The
// pages are served as static files by App Engine, so the backend never sees
// the request and cannot redirect it; the domain's DNS cannot either. So the
// page sends the visitor on to the same path on www, before anything loads.
export default defineNuxtPlugin(() => {
  const { hostname, pathname, search, hash } = window.location
  if (hostname === "frbe-kbsb-ksb.be") {
    window.location.replace(`https://www.frbe-kbsb-ksb.be${pathname}${search}${hash}`)
  }
})
