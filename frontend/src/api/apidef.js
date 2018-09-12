export default {
  // per api call define the required parameters per type

  // members
  getMembers: {
    method: 'GET',
    url: '/members/member',
    query: ['ss', 'start', 'count', 'cat'],
    required: [],
  },

  // rating lists
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
