'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  getUserName, 
  getUserId, 
  getUserIcon, 
  setUser as setStorageUser, 
  clearUser as clearStorageUser 
} from '../utils/userStorage';

interface User {
  id: string;
  name: string;
  icon?: string;
}

interface UserContextType {
  user: User | null;
  isLoading: boolean;
  login: (id: string, name: string, icon?: string) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize from local storage
    const id = getUserId();
    const name = getUserName();
    const icon = getUserIcon();

    if (id && name) {
      setUser({ id, name, icon: icon || undefined });
    }
    setIsLoading(false);
  }, []);

  const login = (id: string, name: string, icon?: string) => {
    setStorageUser(id, name, icon);
    setUser({ id, name, icon });
  };

  const logout = () => {
    clearStorageUser();
    setUser(null);
  };

  return (
    <UserContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

