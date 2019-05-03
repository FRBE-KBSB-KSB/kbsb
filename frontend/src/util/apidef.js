export default {
  // per api call define the required parameters per type

  // article
  getArticles: {
    method: 'GET',
    url: '/articles',
    query: ['ss', 'cat'],
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

};
