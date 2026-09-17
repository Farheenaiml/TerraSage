let rawBaseUrl = import.meta.env.VITE_API_BASE_URL || '';

// If running in production on render.com and VITE_API_BASE_URL wasn't provided at build time:
if (!rawBaseUrl && typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')) {
  rawBaseUrl = 'https://terrasage-backend.onrender.com';
}

if (rawBaseUrl && !rawBaseUrl.startsWith('http://') && !rawBaseUrl.startsWith('https://')) {
  rawBaseUrl = `https://${rawBaseUrl}`;
}
const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export async function mockDelay<T>(data: T, ms = 600): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}

export interface RequestOptions {
  signal?: AbortSignal;
}

async function request<T>(
  path: string,
  options: RequestInit & RequestOptions = {},
): Promise<T> {
  const targetBase = API_BASE_URL || (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com') ? 'https://terrasage-backend.onrender.com' : '');
  
  if (!targetBase) {
    throw new Error(
      'VITE_API_BASE_URL is not configured. Services are running in mock mode.',
    );
  }

  const { signal, ...init } = options;
  const url = `${targetBase}${path.startsWith('/') ? path : `/${path}`}`;
  const response = await fetch(url, {
    ...init,
    signal,
    headers: {
      'Content-Type': 'application/json',
      ...init.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export { request, API_BASE_URL };
