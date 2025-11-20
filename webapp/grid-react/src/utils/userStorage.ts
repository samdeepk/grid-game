const USER_NAME_KEY = 'grid-game-user-name';
const USER_ID_KEY = 'grid-game-user-id';
const USER_ICON_KEY = 'grid-game-user-icon';

export const getUserName = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(USER_NAME_KEY);
};

export const setUserName = (name: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_NAME_KEY, name);
};

export const getUserIcon = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(USER_ICON_KEY);
};

export const setUserIcon = (icon: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_ICON_KEY, icon);
};

export const hasUserName = (): boolean => {
  return getUserName() !== null;
};

export const getUserId = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(USER_ID_KEY);
};

export const setUserId = (id: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_ID_KEY, id);
};

export const clearUser = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(USER_NAME_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USER_ICON_KEY);
};

export const setUser = (id: string, name: string, icon?: string) => {
  setUserId(id);
  setUserName(name);
  if (icon) setUserIcon(icon);
};

