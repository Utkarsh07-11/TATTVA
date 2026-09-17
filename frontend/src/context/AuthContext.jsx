import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const DEFAULT_GUEST_USER = {
  employee_id: 'MPB260001',
  full_name: 'Rajesh Verma',
  role: 'MINE_OPERATOR',
  tier: 1,
  mine_id: 'MOIL_BALAGHAT',
  state: 'Madhya Pradesh',
  department: 'Balaghat Mine Shift Operations',
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('tattva_user');
      return saved ? JSON.parse(saved) : DEFAULT_GUEST_USER;
    } catch {
      return DEFAULT_GUEST_USER;
    }
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('tattva_token') || 'demo_token_mpb260001';
  });

  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isWeeklyModalOpen, setIsWeeklyModalOpen] = useState(false);
  const [isCommissionModalOpen, setIsCommissionModalOpen] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem('tattva_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('tattva_user');
    }
  }, [user]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('tattva_token', token);
    } else {
      localStorage.removeItem('tattva_token');
    }
  }, [token]);

  const loginWithCredentials = async (employeeId, pin) => {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ employee_id: employeeId, pin }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }
      setUser(data.user);
      setToken(data.token);
      setIsLoginModalOpen(false);
      return { success: true, user: data.user };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const logout = () => {
    setUser(DEFAULT_GUEST_USER);
    setToken('demo_token_mpb260001');
    localStorage.removeItem('tattva_user');
    localStorage.removeItem('tattva_token');
  };

  const quickSwitch = (presetId) => {
    if (presetId === 'TIER1') {
      loginWithCredentials('MPB260001', '123456');
    } else if (presetId === 'TIER2') {
      loginWithCredentials('MHN2601001', '654321');
    } else if (presetId === 'TIER3') {
      loginWithCredentials('IN26009', '999999');
    }
  };

  const value = {
    user,
    token,
    tier: user?.tier || 1,
    role: user?.role || 'MINE_OPERATOR',
    mineId: user?.mine_id || 'MOIL_BALAGHAT',
    isSiteOperator: user?.tier === 1,
    isExecutive: user?.tier >= 2,
    isApex: user?.tier === 3,
    loginWithCredentials,
    logout,
    quickSwitch,
    isLoginModalOpen,
    setIsLoginModalOpen,
    isWeeklyModalOpen,
    setIsWeeklyModalOpen,
    isCommissionModalOpen,
    setIsCommissionModalOpen,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
