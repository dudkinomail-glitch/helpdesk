const trimTrailingSlash = (value: string): string => value.replace(/\/$/, '');

const browserHost = (): string => {
  if (typeof window === 'undefined') {
    return 'localhost';
  }
  return window.location.hostname;
};

export const apiBaseUrl = (): string => {
  const fromEnv = import.meta.env.VITE_API_URL as string | undefined;
  if (fromEnv && fromEnv.length > 0) {
    return trimTrailingSlash(fromEnv);
  }
  return `http://${browserHost()}:8000/api`;
};

export const wsEventsUrl = (): string => {
  const fromEnv = import.meta.env.VITE_WS_URL as string | undefined;
  if (fromEnv && fromEnv.length > 0) {
    return fromEnv;
  }
  return `ws://${browserHost()}:8000/ws/events`;
};
