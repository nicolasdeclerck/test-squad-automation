import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    const res = await api.get("/api/accounts/me/");
    if (res.ok && res.data.id) {
      setUser(res.data);
    } else {
      setUser(null);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (email, password) => {
    const res = await api.post("/api/accounts/login/", { email, password });
    if (res.ok) {
      setUser(res.data);
    }
    return res;
  };

  const signup = async (email, password1, password2) => {
    const res = await api.post("/api/accounts/signup/", {
      email,
      password1,
      password2,
    });
    if (res.ok) {
      setUser(res.data);
    }
    return res;
  };

  const logout = async () => {
    await api.post("/api/accounts/logout/");
    setUser(null);
  };

  const updateProfile = async (formData) => {
    const res = await api.put("/api/accounts/profile/", formData);
    if (res.ok) {
      setUser(res.data);
    }
    return res;
  };

  const deleteAvatar = async () => {
    const res = await api.delete("/api/accounts/avatar/delete/");
    if (res.ok) {
      setUser((prev) => ({ ...prev, avatar: null }));
    }
    return res;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        signup,
        logout,
        updateProfile,
        deleteAvatar,
        fetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
