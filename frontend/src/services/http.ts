const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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
  if (!API_BASE_URL) {
    throw new Error(
      'VITE_API_BASE_URL is not configured. Services are running in mock mode.',
    );
  }

  const { signal, ...init } = options;
  const response = await fetch(`${API_BASE_URL}${path}`, {
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
