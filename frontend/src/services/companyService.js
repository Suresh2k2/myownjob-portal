import api from "./api";

export const companyService = {
  list(params = {}) {
    return api.get("/companies/", { params });
  },
  getMy() {
    return api.get("/companies/me");
  },
  get(id) {
    return api.get(`/companies/${id}`);
  },
  create(data) {
    return api.post("/companies/", data);
  },
};
