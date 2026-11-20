// Helpers for resized product images.
// The admin upload stores "<key>-w<width>.webp" variants next to the original and the
// Cloudflare Worker serves them for "?w=<width>" (falling back to the original file when a
// variant does not exist, e.g. for images uploaded before variants were introduced).
// Keep VARIANT_WIDTHS in sync with cloudflare-worker/worker.js and app/images/router.py.

export const VARIANT_WIDTHS = [200, 480, 800] as const;

/** Add ?w=<width> to a CDN url (works with or without an existing ?v=). Empty url stays empty. */
export const imageWithWidth = (url: string | null | undefined, width: number): string => {
  if (!url) return '';
  return `${url}${url.includes('?') ? '&' : '?'}w=${width}`;
};

/** srcset string for the given widths, e.g. "<url>&w=480 480w, <url>&w=800 800w". */
export const imageSrcset = (
  url: string | null | undefined,
  widths: readonly number[] = VARIANT_WIDTHS
): string => {
  if (!url) return '';
  return widths.map((w) => `${imageWithWidth(url, w)} ${w}w`).join(', ');
};

