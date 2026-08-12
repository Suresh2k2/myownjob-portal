import api from "./api";

export const applicationService = {
  create(data) {
    return api.post("/applications/", data);
  },
  listMy() {
    return api.get("/applications/me");
  },
  listForJob(jobId) {
    return api.get(`/applications/job/${jobId}`);
  },
  updateStatus(id, status) {
    return api.put(`/applications/${id}/status`, { status });
  },
};
