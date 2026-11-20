
import api from "./api";

const authService = {
  // Register new student
  register: async (userData) => {
    const response = await api.post("/register", userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    const response = await api.post("/login", credentials);

    const token = response.data.token || response.data.access_token;

    if (token) {
      localStorage.setItem("token", token);
    }

    return response.data;
  },

  // Get logged-in user profile
  getProfile: async () => {
    const response = await api.get("/profile");
    return response.data;
  },

  // Update profile
  updateProfile: async (userData) => {
    const response = await api.put("/profile", userData);
    return response.data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem("token");
  },
};

export default authService;

