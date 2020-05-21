module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  "devServer": {
    "proxy": {
      "/api": {
        "target": "http://localhost:8000"
      },
      "/openapi.json": {
        "target": "http://localhost:8000"
      }
    }
  },
  "pages": {
    "mgmt": {
      "entry": "src/mgmt/index.js"
    },
    "page": {
      "entry": "src/page/index.js",
    }
  }
}