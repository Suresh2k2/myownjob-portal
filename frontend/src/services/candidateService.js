import api from "./api";

export const candidateService = {
  getProfile() {
    return api.get("/candidates/me/profile");
  },
  createProfile(data) {
    return api.post("/candidates/me/profile", data);
  },
  updateProfile(data) {
    return api.put("/candidates/me/profile", data);
  },
};
