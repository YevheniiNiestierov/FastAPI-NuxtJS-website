// Per-page <title>, meta description, canonical, hreflang and Open Graph tags.
// Canonical is built from the current route path (query string dropped), not a single root URL.
export interface PageSeoOptions {
  title: string;
  description: string;
  image?: string;
  type?: 'website' | 'product' | 'article';
  noindex?: boolean;
}

export const usePageSeo = (options: PageSeoOptions | (() => PageSeoOptions)) => {
  const route = useRoute();
  const config = useRuntimeConfig();
  const siteUrl = String(config.public.siteUrl).replace(/\/$/, '');
  const read = () => (typeof options === 'function' ? options() : options);

  const canonical = computed(() => {
    const path = route.path === '/' ? '' : route.path.replace(/\/$/, '');
    return `${siteUrl}${path}` || siteUrl;
  });

  useHead(() => {
    const o = read();
    return {
      title: o.title,
      link: [
        { rel: 'canonical', href: canonical.value },
        { rel: 'alternate', hreflang: 'uk-UA', href: canonical.value }
      ]
    };
  });

  useSeoMeta({
    description: () => read().description,
    robots: () => (read().noindex ? 'noindex, nofollow' : 'index, follow'),
    ogTitle: () => read().title,
    ogDescription: () => read().description,
    ogType: () => (read().type === 'product' ? 'website' : read().type || 'website'),
    ogUrl: () => canonical.value,
    ogLocale: 'uk_UA',
    ogSiteName: 'Natur Savon',
    ogImage: () => read().image,
    twitterCard: 'summary_large_image'
  });
};

