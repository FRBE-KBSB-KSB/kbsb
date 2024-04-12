import axios from "axios";

const prefix = "/api/v1/content";
export default {
  anon_get_articles: async function () {
    const resp = await axios.get(`${prefix}/anon/article`, {});
    return resp;
  },

  anon_get_article: async function (options) {
    const { slug } = options;
    const resp = await axios.get(`${prefix}/anon/article/${slug}`);
    return resp;
  },
};
