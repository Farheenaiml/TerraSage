import { afterEach, describe, expect, it, vi } from 'vitest';
import { getRequestErrorMessage, request } from './http';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('HTTP service errors', () => {
  it('uses the FastAPI detail when a request fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Database operation failed.' }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    );

    await expect(request('/api/dashboard')).rejects.toThrow('Database operation failed.');
  });

  it('keeps the page context when formatting a request error', () => {
    expect(
      getRequestErrorMessage(
        new Error('Database operation failed.'),
        'Failed to load dashboard data.',
      ),
    ).toBe('Failed to load dashboard data. Database operation failed.');
  });
});
