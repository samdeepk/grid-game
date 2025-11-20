'use client';

import React, { ReactNode } from 'react';
import { UserProvider } from '../src/context/UserContext';
import { ToastProvider } from '../src/context/ToastContext';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ToastProvider>
      <UserProvider>
        {children}
      </UserProvider>
    </ToastProvider>
  );
}

