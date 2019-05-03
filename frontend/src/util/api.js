import schemas from './apidef';
import axios from 'axios';
import _ from 'lodash';

axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = 'csrftoken';

// uses config.api_url

export default function(name, params) {

  let schema, surl, options, _body = undefined,
      body = {}, sbody,
      headers = {}, sheaders,
      query= {}, squery,
      path= {}, spath,
      all = {};

  schema = schemas[name];
  if (!schema) {
    console.error('api not called: schema ' + name + 'not found:');
    return Promise.reject(new Error('schama ' + name + ' not found'))
  }

  // fill in all parameters
  sbody = schema.body || [];
  sheaders = schema.headers || [];
  squery = schema.query || [];
  spath = schema.path || [];
  _.forEach(params, function(v, k){
    if (k == '_body') {
      _body = v;
      return;
    }
    if (sbody.indexOf(k) !== -1) {
      all[k] = true;
      body[k] = v;
      return;
    }
    if (sheaders.indexOf(k) !== -1) {
      all[k] = true;
      headers[k] = v;
      return
    }
    if (squery.indexOf(k) !== -1) {
      all[k] = true;
      if (v !== null)
        query[k] = v;
      return;
    }
    if (spath.indexOf(k) !== -1) {
      all[k] = true;
      path[k] = v;
      return;
    }
  });

    // check required paramaters
  if (schema.required) {
    if (!schema.required.every(function(k){
      if (k in params) return true;
      console.error('server not called: missing_param', k);
      return false
    })) {
      return Promise.reject(new Error('missing_param'));
    }
  }

  // set axios options dict
  surl = schema.url;
  _.forEach(path, function(val, pp){
    surl = surl.replace('{' + pp + '}', val)
  });
  headers['Accept'] = 'application/json';
  headers['Content-Type'] = 'application/json';
  options = {
    method: schema.method,
    url: window.config.api_url +  surl,
    params: query,
    data: (_body === undefined) ? body : _body,
    headers: headers
  };

  // make http call in a Promise
  console.log('calling api', name, params);
  return new Promise(function(resolve, reject){
    axios.request(options).then(
      function(data){
        console.log('api call', name, 'successful', data);
        resolve(data.data);
      },
      function(data){
        console.log('api call', name, 'failed', data.response);
        reject(data.response);
      }
    )
  });

}
