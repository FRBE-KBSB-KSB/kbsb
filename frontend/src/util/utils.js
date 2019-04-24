import * as moment from 'moment'
import 'moment/locale/nl'
import 'moment/locale/fr'
import 'moment/locale/de'

function formatDate(d){
  return d ? moment(d).format('DD MMMM YYYY'): ''
}

export {formatDate};