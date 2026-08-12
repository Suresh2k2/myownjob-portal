import api from "./api";

export const authService = {
  register(data) {
    return api.post("/auth/register", data);
  },
  login(email, password) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);
    return api.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  refreshToken(refresh_token) {
    return api.post("/auth/refresh", { refresh_token });
  },
  getMe() {
    return api.get("/users/me");
  },
};
