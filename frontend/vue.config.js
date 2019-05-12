// vue.config.js

const BundleTracker  = require('webpack-bundle-tracker');

module.exports = {
  configureWebpack: {
    plugins: [
      new BundleTracker({
        indent: 2,
        publicPath: process.env.NODE_ENV === 'production' ? '/static/' : 
          'http://localhost:8080/static/',
        // path: process.env.NODE_ENV === 'production' ? '.' : '../build/static/'
      })
    ],
    devServer: {
      publicPath: '/static',
      port: 8080,
    }
  },
  outputDir: 'dist/static',
  publicPath: '/static/',
  crossorigin: "anonymous",
  runtimeCompiler: true,
  pages: {
    cms: 'src/cms.js',
    mgmt: 'src/mgmt.js',
    article: 'src/article.js',
    articles: 'src/articles.js',
  },

}
  