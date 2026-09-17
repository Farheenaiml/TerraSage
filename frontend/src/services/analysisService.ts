import type {
  AnalysisRecord,
  AnalysisRequest,
  AnalysisResult,
} from '@/models';
import { request, mockDelay, API_BASE_URL } from './http';
import { mockAnalysisResult, mockAnalyses } from '@/data/analysis';

export const analysisService = {
  async getAnalyses(): Promise<AnalysisRecord[]> {
    if (!API_BASE_URL) {
      return mockDelay(mockAnalyses);
    }
    return request<AnalysisRecord[]>('/analyses');
  },

  async getAnalysis(id: string): Promise<AnalysisResult> {
    if (!API_BASE_URL) {
      return mockDelay(mockAnalysisResult, 900);
    }
    return request<AnalysisResult>(`/analyses/${id}`);
  },

  async submitAnalysis(req: AnalysisRequest): Promise<AnalysisResult> {
    if (!API_BASE_URL) {
      return mockDelay(mockAnalysisResult, 1200);
    }
    return request<AnalysisResult>('/analyses', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },
};
