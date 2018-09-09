export default {
  // per api call define the required parameters per type

  //attendee
  getMembers: {
    method: 'GET',
    url: '/api/members',
    query: ['ss', 'start', 'count', 'cat'],
    required: [],
  },

  // chess members
  searchIdNational: {
    method: 'GET',
    url: '/belplayer/{idbel}',
    path: ['idbel'],
    required: ['idbel'],
  },
  searchIdFide: {
    method: 'GET',
    url: '/fideplayer/{idfide}',
    path: ['idfide'],
    required: ['idfide'],
  },

};
