const USER_NAME_KEY = 'grid-game-user-name';

export const getUserName = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(USER_NAME_KEY);
};

export const setUserName = (name: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_NAME_KEY, name);
};

export const hasUserName = (): boolean => {
  return getUserName() !== null;
};

