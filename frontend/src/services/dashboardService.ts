import type { DashboardData } from '@/models';
import { request } from './http';
import { normalizeProfile } from './environmentService';

export const dashboardService = {
  async getDashboard(): Promise<DashboardData> {
    return request<any>('/api/dashboard').then((response) => ({
      ...response,
      profile: normalizeProfile(response.profile),
    }));
  },
};
