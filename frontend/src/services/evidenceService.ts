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
    const sources = await request<any[]>(filter?.query ? '/api/knowledge/search' : '/api/knowledge/sources', filter?.query ? {
      method: 'POST',
      body: JSON.stringify({ query: filter.query, top_k: 20, metrics: filter.metric ? [filter.metric] : [] }),
    } : undefined);
    const items = filter?.query ? (sources as any).results : sources;
    return items.map((item: any) => ({
      id: item.id || item.chunkId,
      title: item.title,
      source: item.sourceType,
      organization: item.organization,
      year: item.year || 0,
      type: item.sourceType as EvidenceType,
      metrics: item.environmentalMetrics || item.matchedMetrics || [],
      url: item.sourceUrl,
      summary: item.text || item.topic || `${item.ingestionStatus} source`,
      relevanceScore: item.relevanceScore,
    }));
  },

  async getEvidenceById(id: string): Promise<EvidenceReference> {
    const sources = await request<any[]>('/api/knowledge/sources');
    const item = sources.find((source) => source.id === id);
    if (!item) throw new Error('Evidence source not found.');
    return {
      id: item.id,
      title: item.title,
      source: item.sourceType,
      organization: item.organization,
      year: item.year || 0,
      type: item.sourceType as EvidenceType,
      metrics: item.environmentalMetrics || [],
      url: item.sourceUrl,
      summary: item.topic,
    };
  },
};
