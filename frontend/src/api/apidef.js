export default {
  // per api call define the required parameters per type

  // members
  getMembers: {
    method: 'GET',
    url: '/members/member',
    query: ['ss', 'start', 'count', 'cat'],
    required: [],
  },
  addMember: {
    method: 'POST',
    url: '/members/member',
    body: ['member'],
    required: ['member'],
  },
  saveMember: {
    method: 'PUT',
    url: '/members/member/{idbel}',
    path: ['idbel'],
    body: ['member'],
    required: ['member', 'idbel'],
  },
  delMember: {
    method: 'DELETE',
    url: '/members/member/{idbel}',
    path: ['idbel'],
    required: ['idbel'],
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
