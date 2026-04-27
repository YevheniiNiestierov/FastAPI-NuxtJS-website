/**
 * Cloudflare Worker: s3-image-proxy
 * Route: assets.natur-savon.com.ua/*
 *
 * Fetches images from S3 and caches them at the Cloudflare edge.
 * No credentials needed — the S3 bucket policy allows public reads.
 */
export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const s3Url = `https://natur-savon-images.s3.eu-north-1.amazonaws.com${url.pathname}`;

    const response = await fetch(s3Url, {
      method: request.method,
      cf: {
        cacheTtl: 31536000,
        cacheEverything: true
      }
    });

    return new Response(response.body, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'image/webp',
        'Cache-Control': 'public, max-age=31536000, immutable',
        'Access-Control-Allow-Origin': '*',
      }
    });
  }
};

