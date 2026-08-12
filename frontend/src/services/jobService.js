import api from "./api";

export const jobService = {
  list(params = {}) {
    return api.get("/jobs/", { params });
  },
  get(id) {
    return api.get(`/jobs/${id}`);
  },
  create(data) {
    return api.post("/jobs/", data);
  },
  update(id, data) {
    return api.put(`/jobs/${id}`, data);
  },
  delete(id) {
    return api.delete(`/jobs/${id}`);
  },
};
