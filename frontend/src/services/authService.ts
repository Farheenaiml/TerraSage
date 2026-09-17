import type { AuthSession, LoginCredentials, SignupData, User } from '@/models';
import { mockDelay } from './http';
import { mockUser } from '@/data/user';

const TOKEN_KEY = 'terrasage_token';
const USER_KEY = 'terrasage_user';

function storeSession(session: AuthSession) {
  localStorage.setItem(TOKEN_KEY, session.token);
  localStorage.setItem(USER_KEY, JSON.stringify(session.user));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthSession> {
    // Demo mode: local session per Chunk 1 architecture
    const user: User = {
      ...mockUser, fullName: 'Zoya Patel', organization: 'Conservation Trust',
      email: credentials.email || mockUser.email,
    };
    const session: AuthSession = { user, token: 'session-' + Date.now() };
    storeSession(session);
    return mockDelay(session, 300);
  },

  async signup(data: SignupData): Promise<AuthSession> {
    // Demo mode: stores user locally per Chunk 1 architecture
    const user: User = {
      id: 'user-' + Date.now(),
      email: data.email,
      fullName: data.fullName,
      organization: data.organization || 'Conservation Trust',
      role: 'Environmental Scientist',
      createdAt: new Date().toISOString(),
    };
    const session: AuthSession = { user, token: 'session-' + Date.now() };
    storeSession(session);
    return mockDelay(session, 300);
  },

  async logout(): Promise<void> {
    clearSession();
  },

  getCurrentUser(): User | null {
    return getStoredUser();
  },

  getToken(): string | null {
    return getStoredToken();
  },

  isAuthenticated(): boolean {
    return getStoredToken() !== null;
  },
};
