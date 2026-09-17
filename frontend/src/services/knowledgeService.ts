import { request } from './http';

export interface KnowledgeSearchResult {
  documentId: string;
  title: string;
  organization: string;
  year: number | null;
  sourceType: string;
  sourceUrl: string;
  chunkId: string;
  text: string;
  relevanceScore: number;
  matchedMetrics: string[];
}

export const knowledgeService = {
  async search(query: string, topK = 5, metrics: string[] = []): Promise<KnowledgeSearchResult[]> {
    const response = await request<{ results: KnowledgeSearchResult[] }>('/api/knowledge/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK, metrics }),
    });
    return response.results;
  },
};
