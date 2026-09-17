// ===== Auth =====
export interface User {
  id: string;
  email: string;
  fullName: string;
  avatarUrl?: string;
  organization?: string;
  role: string;
  createdAt: string;
}

export interface AuthSession {
  user: User;
  token: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  fullName: string;
  organization?: string;
}

// ===== Environmental Data =====
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type TimeHorizon = 'short-term' | 'medium-term' | 'long-term';

export interface SoilData {
  ph: number | null;
  organicCarbonPercent: number | null;
  moisturePercent: number | null;
  texture?: string | null;
  nutrientLevels?: {
    nitrogen?: number | null;
    phosphorus?: number | null;
    potassium?: number | null;
  } | null;
  source?: string | null;
  depth?: string | null;
}

export interface ClimateData {
  annualRainfallMm: number | null;
  avgTemperatureC: number | null;
  temperatureRange?: { min: number | null; max: number | null } | null;
  humidityPercent?: number | null;
  growingSeasonDays?: number | null;
  temperatureSource?: string | null;
  rainfallSource?: string | null;
  temperaturePeriod?: { start?: string | null; end?: string | null } | null;
  rainfallPeriod?: { start?: string | null; end?: string | null } | null;
}

export interface LandData {
  landUseType: string | null;
  coverType: string | null;
  areaHectares?: number | null;
  slope?: string | null;
  erosionRisk?: 'low' | 'moderate' | 'high' | null;
  source?: string | null;
}

export interface BiodiversityData {
  speciesRichness: number | null;
  habitatDiversityIndex: number | null;
  endemicSpecies?: number | null;
  invasiveSpecies?: number | null;
  protectedAreaPercent?: number | null;
  source?: string | null;
  observationCount?: number | null;
}

export interface HumanImpactData {
  pollutionIndex: number | null;
  deforestationRatePercent: number | null;
  populationDensityPerKm2?: number | null;
  industrialActivity?: string | null;
  waterStressLevel?: 'low' | 'moderate' | 'high' | 'severe' | null;
  pm2_5?: number | null;
  pm2_5_unit?: string | null;
  pm2_5_source?: string | null;
  pm10?: number | null;
  pm10_unit?: string | null;
  pm10_source?: string | null;
  aqi?: number | null;
  europeanAqi?: number | null;
  usAqi?: number | null;
  treeCoverLossHa?: number | null;
  treeCoverLossSource?: string | null;
  forestChangePeriod?: string | null;
}

export interface EnvironmentalProfile {
  id: string;
  userId?: string;
  locationName?: string;
  region?: string | null;
  latitude: number | null;
  longitude: number | null;
  soil: SoilData;
  climate: ClimateData;
  land: LandData;
  biodiversity: BiodiversityData;
  humanImpact: HumanImpactData;
  updatedAt: string;
  completenessPercent?: number;
}

// ===== Analysis =====
export type AnalysisMode = 'natural-language' | 'structured';
export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface AnalysisRequest {
  mode: AnalysisMode;
  naturalLanguageQuery?: string;
  structuredData?: Partial<EnvironmentalProfile>;
}

export interface DetectedFactor {
  id: string;
  category: 'soil' | 'climate' | 'land' | 'biodiversity' | 'human-impact';
  name: string;
  value: string;
  status: 'optimal' | 'adequate' | 'suboptimal' | 'critical' | 'unknown';
  description: string;
}

export interface MetricRelationship {
  id: string;
  metricA: string;
  metricB: string;
  relationship: 'positive' | 'negative' | 'neutral';
  strength: 'strong' | 'moderate' | 'weak';
  description: string;
}

export interface ImpactedMetric {
  id: string;
  metric: string;
  category: 'soil' | 'climate' | 'land' | 'biodiversity' | 'human-impact';
  currentValue: string;
  projectedValue: string;
  changeDirection: 'increase' | 'decrease' | 'stabilize';
  changeMagnitude: string;
}

export interface MissingInfoItem {
  id: string;
  field: string;
  category: 'soil' | 'climate' | 'land' | 'biodiversity' | 'human-impact' | 'location';
  question: string;
  importance: 'critical' | 'important' | 'optional';
}

export interface AnalysisResult {
  id: string;
  status: AnalysisStatus;
  assessmentSummary: string;
  overallHealthScore: number;
  detectedFactors: DetectedFactor[];
  metricRelationships: MetricRelationship[];
  recommendations: AnalysisRecommendation[];
  impactedMetrics: ImpactedMetric[];
  timeHorizon: {
    short: string;
    medium: string;
    long: string;
  };
  confidence: ConfidenceLevel;
  confidenceScore: number;
  scientificEvidence: EvidenceReference[];
  missingInformation: MissingInfoItem[];
  createdAt: string;
}

export interface AnalysisRecommendation {
  id: string;
  title: string;
  rationale: string;
  impactedMetrics: string[];
  expectedImpact: string;
  timeHorizon: TimeHorizon;
  confidence: ConfidenceLevel;
  evidenceIds: string[];
}

export interface AnalysisRecord {
  id: string;
  mode: AnalysisMode;
  query: string;
  status: AnalysisStatus;
  locationName: string;
  healthScore: number;
  createdAt: string;
  resultSummary: string;
}

// ===== Recommendations =====
export interface Recommendation {
  id: string;
  title: string;
  description: string;
  rationale: string;
  impactedMetrics: string[];
  expectedImpact: string;
  timeHorizon: TimeHorizon;
  confidence: ConfidenceLevel;
  confidenceScore: number | null;
  confidenceRationale?: string;
  limitations?: string[];
  relationshipId?: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  evidence: EvidenceReference[];
  status: 'suggested' | 'in-progress' | 'implemented' | 'dismissed';
  createdAt: string;
  analysisId?: string;
}

// ===== Evidence =====
export type EvidenceType =
  | 'peer-reviewed'
  | 'government-report'
  | 'ngo-report'
  | 'dataset'
  | 'guideline'
  | 'meta-analysis';

export interface EvidenceReference {
  id: string;
  title: string;
  source: string;
  organization: string;
  year: number;
  type: EvidenceType;
  metrics: string[];
  url: string;
  summary: string;
  relevanceScore?: number;
}

// ===== Conversations =====
export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  evidenceRefs?: string[];
  analysisRef?: string;
}

export interface EnvironmentalContext {
  known: { category: string; field: string; value: string }[];
  missing: { category: string; field: string; question: string }[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: ConversationMessage[];
  environmentalContext: EnvironmentalContext;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

// ===== Dashboard =====
export interface DashboardOverview {
  availableFactors: number;
  missingFactors: number;
}

export interface EnvironmentalInteraction {
  id: string;
  source: string;
  target: string;
  interaction: string;
  type: 'positive' | 'negative' | 'neutral';
}

export interface DashboardData {
  profile: EnvironmentalProfile | null;
  availableFields: string[];
  missingFields: string[];
  recentAnalyses: AnalysisRecord[];
  recommendations: Recommendation[];
  evidenceSummary: { total: number; byType: Record<string, number>; recentCount: number };
}

// ===== Generic API =====
export interface ApiError {
  message: string;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
