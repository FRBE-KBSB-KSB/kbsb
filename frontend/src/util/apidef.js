export default {
  // per api call define the required parameters per type

  // article
  getArticles: {
    method: 'GET',
    url: '/articles',
    query: ['ss'],
    required: [],
  },
  addArticle: {
    method: 'POST',
    url: '/articles',
    body: ['article'],
    required: ['article'],
  },
  getArticle: {
    method: 'GET',
    url: '/articles/{id}',
    path: ['id'],
    required: ['id'],
  },
  deleteArticle: {
    method: 'DELETE',
    url: '/articles/{id}',
    path: ['id'],
    required: ['id'],
  },
  updateArticle: {
    method: 'PUT',
    url: '/articles/{id}',
    path: ['id'],
    body: ['article'],
    required: ['article', 'id'],
  },

  // Members
  getMembers: {
    method: 'GET',
    url: '/members',
    query: ['ss', 'cat', 'count', 'start'],
    required: [],
  },
  addMember: {
    method: 'POST',
    url: '/members',
    body: ['member'],
    required: ['member'],
  },
  getMember: {
    method: 'GET',
    url: '/members/{id}',
    path: ['id'],
    required: ['id'],
  },
  deleteMember: {
    method: 'DELETE',
    url: '/members/{id}',
    path: ['id'],
    required: ['id'],
  },
  updateMember: {
    method: 'PUT',
    url: '/members/{id}',
    path: ['id'],
    body: ['member'],
    required: ['member', 'id'],
  },
  getGroupRoles: {
    method: 'GET',
    url: '/grouproles',
    required: [],
  },
  updateGroupRoles: {
    method: 'PUT',
    url: '/grouproles',
    body: ['groupnames', 'rolenames'],
    required: ['groupnames', 'rolenames'],
  },
  uploadPhoto: {
    method: 'POST',
    url: '/members/{id}/photo',
    body: ['photo'],
    path: ['id'],
    required: ['photo', 'id']    
  }

};
