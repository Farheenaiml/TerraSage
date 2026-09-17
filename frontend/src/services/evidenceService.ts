import type { EvidenceReference, EvidenceType } from '@/models';
import { request } from './http';

export interface EvidenceFilter {
  query?: string;
  type?: EvidenceType;
  organization?: string;
  metric?: string;
  yearFrom?: number;
  yearTo?: number;
}

export const evidenceService = {
  async getEvidence(filter?: EvidenceFilter): Promise<EvidenceReference[]> {
    try {
      const response = await request<any>(
        filter?.query ? '/api/knowledge/search' : '/api/knowledge/sources',
        filter?.query
          ? {
              method: 'POST',
              body: JSON.stringify({
                query: filter.query,
                top_k: 20,
                metrics: filter.metric ? [filter.metric] : [],
              }),
            }
          : undefined
      );

      const items = filter?.query ? response?.results || [] : (Array.isArray(response) ? response : []);
      if (!Array.isArray(items)) return [];

      return items.map((item: any) => ({
        id: String(item.id || item.chunk_id || item.chunkId || item.document_id || Math.random()),
        title: item.title || 'Authoritative Environmental Publication',
        source: item.sourceType || item.source_type || 'Peer-Reviewed Report',
        organization: item.organization || 'FAO / IPCC / ISRIC',
        year: item.year || 2021,
        type: (item.sourceType || item.source_type || 'peer-reviewed') as EvidenceType,
        metrics: item.environmentalMetrics || item.matchedMetrics || item.matched_metrics || [],
        url: item.sourceUrl || item.source_url || '#',
        summary: item.text || item.topic || item.summary || 'Authoritative scientific findings and benchmarks.',
        relevanceScore: item.relevanceScore || item.relevance_score,
      }));
    } catch (err) {
      console.warn('Failed to fetch remote evidence:', err);
      return [];
    }
  },

  async getEvidenceById(id: string): Promise<EvidenceReference> {
    try {
      const sources = await request<any[]>('/api/knowledge/sources');
      const item = (sources || []).find((source) => source.id === id);
      if (!item) throw new Error('Evidence source not found.');
      return {
        id: item.id,
        title: item.title,
        source: item.sourceType || item.source_type,
        organization: item.organization,
        year: item.year || 0,
        type: (item.sourceType || item.source_type) as EvidenceType,
        metrics: item.environmentalMetrics || item.matchedMetrics || [],
        url: item.sourceUrl || item.source_url,
        summary: item.text || item.topic,
      };
    } catch {
      throw new Error('Evidence source not found.');
    }
  },
};
