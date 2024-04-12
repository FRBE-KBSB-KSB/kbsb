export default (context) => ({
  async root() {
    return await fetch.get("/api");
  },
  async login(options) {
    return await fetch.post("/api/v1/accounts/login", options);
  },
});
