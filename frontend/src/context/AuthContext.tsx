import React, { createContext, useContext, useState } from 'react';
import type { AuthState } from '../types';

interface AuthContextType extends AuthState {
  login: (token: string, username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [auth, setAuth] = useState<AuthState>(() => {
    const savedToken = localStorage.getItem('rag_admin_token');
    const savedUser = localStorage.getItem('rag_admin_user');
    return {
      isAuthenticated: !!savedToken,
      token: savedToken,
      username: savedUser,
    };
  });

  const login = (token: string, username: string) => {
    localStorage.setItem('rag_admin_token', token);
    localStorage.setItem('rag_admin_user', username);
    setAuth({
      isAuthenticated: true,
      token,
      username,
    });
  };

  const logout = () => {
    localStorage.removeItem('rag_admin_token');
    localStorage.removeItem('rag_admin_user');
    setAuth({
      isAuthenticated: false,
      token: null,
      username: null,
    });
  };

  return (
    <AuthContext.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
