

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import authService from "../services/authService";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check existing login session
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const data = await authService.getProfile();

        setUser(data.user || data);
      } catch (error) {
        authService.logout();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login
  const login = async (credentials) => {
    const data = await authService.login(credentials);

    if (data.token || data.access_token) {
      const profile = await authService.getProfile();
      setUser(profile.user || profile);
    }

    return data;
  };

  // Register
  const register = async (userData) => {
    return await authService.register(userData);
  };

  // Logout
  const logout = () => {
    authService.logout();
    setUser(null);
  };

  // Update profile
  const updateProfile = async (userData) => {
    const data = await authService.updateProfile(userData);
    setUser(data.user || data);
    return data;
  };

  const value = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    login,
    register,
    logout,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom authentication hook
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}
