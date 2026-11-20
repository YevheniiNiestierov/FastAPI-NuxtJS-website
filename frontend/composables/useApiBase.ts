// API base URL that works in both environments.
// - Browser: public URL (NUXT_PUBLIC_API_BASE).
// - SSR (inside the frontend container): NUXT_API_BASE_INTERNAL (e.g. http://backend:8000) when set,
//   because "localhost:8000" / the public hostname may not be reachable from the container.
export const useApiBase = (): string => {
  const config = useRuntimeConfig();
  if (import.meta.server && config.apiBaseInternal) {
    return String(config.apiBaseInternal).replace(/\/$/, '');
  }
  return String(config.public.apiBase).replace(/\/$/, '');
};

