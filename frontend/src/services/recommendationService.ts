import type { Recommendation, EvidenceReference } from '@/models';
import { request } from './http';

function normalizeEvidence(ev: any): EvidenceReference {
  return {
    id: ev.id || ev.chunkId || 'ev-chunk',
    title: ev.title || 'Authoritative Publication',
    source: ev.source || 'Peer-reviewed literature',
    organization: ev.organization || 'FAO / IPCC',
    year: ev.year || ev.publicationYear || 2020,
    type: ev.type || 'peer-reviewed',
    metrics: ev.metrics || ev.matchedMetrics || [],
    url: ev.url || ev.sourceUrl || '#',
    summary: ev.summary || ev.excerpt || '',
    relevanceScore: ev.relevanceScore !== undefined ? ev.relevanceScore : ev.retrievalScore,
  };
}

function normalizeRecommendation(raw: any): Recommendation {
  const evList = Array.isArray(raw.evidence) ? raw.evidence.map(normalizeEvidence) : [];
  return {
    id: raw.id,
    title: raw.title,
    description: raw.description,
    rationale: raw.rationale,
    impactedMetrics: raw.impactedMetrics || raw.impacted_metrics || [],
    expectedImpact: raw.expectedImpact || raw.expected_impact || '',
    timeHorizon: raw.timeHorizon || raw.time_horizon || 'medium-term',
    confidence: raw.confidence || 'medium',
    confidenceScore: raw.confidenceScore !== undefined ? raw.confidenceScore : (raw.confidence_score !== undefined ? raw.confidence_score : null),
    confidenceRationale: raw.confidenceRationale || raw.confidence_rationale || undefined,
    priority: raw.priority || 'medium',
    category: raw.category || 'ecological',
    evidence: evList,
    status: raw.status || 'suggested',
    limitations: raw.limitations || [],
    relationshipId: raw.relationshipId || raw.relationship_id || undefined,
    createdAt: raw.createdAt || raw.created_at || new Date().toISOString(),
  };
}

export interface GenerateRecommendationsParams {
  reasoningResponse?: any;
  latitude?: number;
  longitude?: number;
  radius_km?: number;
  text_context?: string;
}

export const recommendationService = {
  async getRecommendations(status?: string): Promise<Recommendation[]> {
    const query = status && status !== 'all' ? `?status=${encodeURIComponent(status)}` : '';
    const response = await request<any>(`/api/recommendations${query}`);
    const items = Array.isArray(response) ? response : (response?.items || []);
    return items.map(normalizeRecommendation);
  },

  async getRecommendation(id: string): Promise<Recommendation> {
    const raw = await request<any>(`/api/recommendations/${id}`);
    return normalizeRecommendation(raw);
  },

  async updateStatus(
    id: string,
    status: Recommendation['status'],
  ): Promise<Recommendation> {
    const raw = await request<any>(`/api/recommendations/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
    return normalizeRecommendation(raw);
  },

  async generateRecommendations(params: GenerateRecommendationsParams): Promise<Recommendation[]> {
    const res = await request<{ items: any[]; total: number }>('/api/recommendations/generate', {
      method: 'POST',
      body: JSON.stringify(params),
    });
    return (res.items || []).map(normalizeRecommendation);
  },
};
