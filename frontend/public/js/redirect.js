const l = window.location
if (l.hostname == "bycco.be") {
  location.replace(`${l.protocol}//www.bycco.be${l.pathname}${l.search}`)
}