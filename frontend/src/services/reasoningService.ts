import { request } from './http';

export interface MetricContextDto {
  metric: string;
  value: number | string | null;
  unit?: string | null;
  period?: string | null;
  source?: string | null;
  availability: 'AVAILABLE' | 'UNAVAILABLE' | 'UNKNOWN' | 'NOT_APPLICABLE' | string;
  unavailabilityReason?: string | null;
  metadata?: Record<string, any>;
}

export interface LinkedEvidenceDto {
  documentId: string;
  chunkId: string;
  source: string;
  title: string;
  organization: string;
  publicationYear?: number | null;
  excerpt: string;
  retrievalScore: number;
  sourceUrl?: string | null;
  matchedMetrics: string[];
}

export interface EnvironmentalRelationshipDto {
  relationshipId: string;
  relationshipType: string;
  title: string;
  metrics: string[];
  metricsCount: number;
  isMultiMetric: boolean;
  fallbackLabel?: string | null;
  interpretation: string;
  evidenceStatus: 'supported' | 'insufficient_evidence' | string;
  evidence: LinkedEvidenceDto[];
  limitations: string[];
}

export interface ReasoningResponseDto {
  location: {
    latitude: number;
    longitude: number;
    radiusKm: number;
    [key: string]: any;
  };
  userContext: Record<string, any>;
  availableMetrics: MetricContextDto[];
  unavailableMetrics: MetricContextDto[];
  relationships: EnvironmentalRelationshipDto[];
  overallInterpretation: string;
  limitations: string[];
}

export interface ReasoningRequestDto {
  latitude: number;
  longitude: number;
  radius_km?: number;
  context?: Record<string, any>;
  text_context?: string;
}

export const reasoningService = {
  async analyze(req: ReasoningRequestDto): Promise<ReasoningResponseDto> {
    return request<ReasoningResponseDto>('/api/reasoning/analyze', {
      method: 'POST',
      body: JSON.stringify(req),
    });
  },
};
