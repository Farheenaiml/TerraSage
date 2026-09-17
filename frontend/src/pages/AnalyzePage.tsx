import { useState } from 'react';
import {
  Microscope,
  FileText,
  MapPin,
  Loader2,
  AlertCircle,
  Info,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  BookOpen,
  HelpCircle,
  Activity,
  Lightbulb,
  CheckCircle2,
  ExternalLink,
  Database,
  Layers,
  ShieldAlert,
} from 'lucide-react';
import type { AnalysisMode, AnalysisRequest, AnalysisResult } from '@/models';
import { analysisService } from '@/services';
import { knowledgeService, type KnowledgeSearchResult } from '@/services/knowledgeService';
import {
  recommendationService,
  reasoningService,
  type ReasoningResponseDto,
  type EnvironmentalRelationshipDto,
  type MetricContextDto,
  type LinkedEvidenceDto,
} from '@/services';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { ConfidenceBadge, StatusIndicator, TimeHorizonBadge } from '@/components/shared/Badges';
import { EvidenceCard } from '@/components/shared/EvidenceCard';
import { RecommendationCard } from '@/components/shared/RecommendationCard';
import type { Recommendation } from '@/models';
import { HealthScoreRing } from '@/components/shared/HealthScoreRing';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

type PageMode = 'multi-metric' | 'natural-language' | 'structured';

export function AnalyzePage() {
  const [activeTab, setActiveTab] = useState<PageMode>('multi-metric');

  // Multi-metric reasoning state
  const [reasoningLat, setReasoningLat] = useState('19.0760');
  const [reasoningLon, setReasoningLon] = useState('72.8777');
  const [reasoningRadius, setReasoningRadius] = useState('10');
  const [userContextText, setUserContextText] = useState('');
  const [reasoningLoading, setReasoningLoading] = useState(false);
  const [reasoningError, setReasoningError] = useState('');
  const [reasoningResult, setReasoningResult] = useState<ReasoningResponseDto | null>(null);

  // Natural language state
  const [naturalLanguage, setNaturalLanguage] = useState('');
  const [retrievalResults, setRetrievalResults] = useState<KnowledgeSearchResult[]>([]);
  const [retrievalLoading, setRetrievalLoading] = useState(false);
  const [retrievalError, setRetrievalError] = useState('');

  // Legacy structured state (Chunk 1 mock fallback)
  const [structuredLoading, setStructuredLoading] = useState(false);
  const [structuredError, setStructuredError] = useState('');
  const [structuredResult, setStructuredResult] = useState<AnalysisResult | null>(null);
  const [structured, setStructured] = useState({
    locationName: '',
    latitude: '',
    longitude: '',
    soilPh: '',
    soilOrganicCarbon: '',
    soilMoisture: '',
    annualRainfall: '',
    avgTemperature: '',
    landUse: '',
    speciesRichness: '',
    pollutionIndex: '',
    deforestationRate: '',
  });

  const handleRunReasoning = async () => {
    const lat = parseFloat(reasoningLat);
    const lon = parseFloat(reasoningLon);
    const radius = parseFloat(reasoningRadius) || 10;

    if (isNaN(lat) || lat < -90 || lat > 90) {
      setReasoningError('Latitude must be a valid number between -90 and 90.');
      return;
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      setReasoningError('Longitude must be a valid number between -180 and 180.');
      return;
    }

    setReasoningLoading(true);
    setReasoningError('');
    setReasoningResult(null);

    try {
      const res = await reasoningService.analyze({
        latitude: lat,
        longitude: lon,
        radius_km: radius,
        text_context: userContextText.trim() || undefined,
      });
      setReasoningResult(res);
    } catch (err) {
      setReasoningError(err instanceof Error ? err.message : 'Multi-metric reasoning failed. Please check backend connection.');
    } finally {
      setReasoningLoading(false);
    }
  };

  const handlePreset = (lat: string, lon: string, context?: string) => {
    setReasoningLat(lat);
    setReasoningLon(lon);
    if (context !== undefined) setUserContextText(context);
  };

  const retrieveKnowledge = async () => {
    if (!naturalLanguage.trim()) return;
    setRetrievalLoading(true);
    setRetrievalError('');
    try {
      setRetrievalResults(await knowledgeService.search(naturalLanguage));
    } catch (error) {
      setRetrievalError(error instanceof Error ? error.message : 'Knowledge retrieval failed.');
      setRetrievalResults([]);
    } finally {
      setRetrievalLoading(false);
    }
  };

  const handleStructuredSubmit = async () => {
    setStructuredLoading(true);
    setStructuredError('');
    setStructuredResult(null);

    const req: AnalysisRequest = {
      mode: 'structured',
      structuredData: {
        locationName: structured.locationName || undefined,
        latitude: structured.latitude ? parseFloat(structured.latitude) : null,
        longitude: structured.longitude ? parseFloat(structured.longitude) : null,
        soil: {
          ph: structured.soilPh ? parseFloat(structured.soilPh) : null,
          organicCarbonPercent: structured.soilOrganicCarbon ? parseFloat(structured.soilOrganicCarbon) : null,
          moisturePercent: structured.soilMoisture ? parseFloat(structured.soilMoisture) : null,
        },
        climate: {
          annualRainfallMm: structured.annualRainfall ? parseFloat(structured.annualRainfall) : null,
          avgTemperatureC: structured.avgTemperature ? parseFloat(structured.avgTemperature) : null,
        },
        land: {
          landUseType: structured.landUse || null,
          coverType: null,
        },
        biodiversity: {
          speciesRichness: structured.speciesRichness ? parseInt(structured.speciesRichness) : null,
          habitatDiversityIndex: null,
        },
        humanImpact: {
          pollutionIndex: structured.pollutionIndex ? parseInt(structured.pollutionIndex) : null,
          deforestationRatePercent: structured.deforestationRate ? parseFloat(structured.deforestationRate) : null,
        },
      },
    };

    try {
      const res = await analysisService.submitAnalysis(req);
      setStructuredResult(res);
    } catch {
      setStructuredError('Failed to run analysis. Please try again.');
    } finally {
      setStructuredLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in">
      <PageHeader
        title="Analyze"
        description="Multi-metric environmental reasoning engine powered by live observations and authoritative scientific literature."
      />

      {/* Mode toggle */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveTab('multi-metric')}
          className={cn(
            'flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors',
            activeTab === 'multi-metric'
              ? 'border-primary bg-primary/5 text-primary shadow-sm font-semibold'
              : 'border-border text-muted-foreground hover:text-foreground',
          )}
        >
          <Layers className="h-4 w-4" />
          Multi-Metric Reasoning (Scientific Engine)
        </button>
        <button
          onClick={() => setActiveTab('natural-language')}
          className={cn(
            'flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors',
            activeTab === 'natural-language'
              ? 'border-primary bg-primary/5 text-primary'
              : 'border-border text-muted-foreground hover:text-foreground',
          )}
        >
          <BookOpen className="h-4 w-4" />
          Evidence Retrieval
        </button>
        <button
          onClick={() => setActiveTab('structured')}
          className={cn(
            'flex items-center gap-2 rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors',
            activeTab === 'structured'
              ? 'border-primary bg-primary/5 text-primary'
              : 'border-border text-muted-foreground hover:text-foreground',
          )}
        >
          <Microscope className="h-4 w-4" />
          Legacy Profile Assessment
        </button>
      </div>

      {/* 1. Multi-Metric Reasoning Mode */}
      {activeTab === 'multi-metric' && (
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                    <Layers className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Scientific Multi-Metric Synthesis</CardTitle>
                    <CardDescription>
                      Fetches live real-world observations across multiple domains simultaneously and grounds cross-domain relationships against peer-reviewed literature.
                    </CardDescription>
                  </div>
                </div>
                <Badge variant="outline" className="border-primary/20 text-primary">
                  Chunk 4 Engine
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-2">
                <Label className="text-xs font-semibold text-muted-foreground">Quick Coordinate Presets</Label>
                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs"
                    onClick={() => handlePreset('19.0760', '72.8777', 'Urban coastal region with high monsoon precipitation')}
                  >
                    Mumbai, India (Urban/Coast)
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs"
                    onClick={() => handlePreset('-1.2921', '36.8219', 'Highland tropical zone with high biodiversity richness')}
                  >
                    Nairobi, Kenya (Highland)
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs"
                    onClick={() => handlePreset('19.8000', '74.4000', 'Intensive cropland agriculture with moderate rainfall')}
                  >
                    Nashik, India (Cropland)
                  </Button>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="space-y-1.5">
                  <Label htmlFor="reasoning-lat" className="text-xs text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5 text-primary" /> Latitude (-90 to 90)
                  </Label>
                  <Input
                    id="reasoning-lat"
                    placeholder="19.0760"
                    value={reasoningLat}
                    onChange={(e) => setReasoningLat(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="reasoning-lon" className="text-xs text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5 text-primary" /> Longitude (-180 to 180)
                  </Label>
                  <Input
                    id="reasoning-lon"
                    placeholder="72.8777"
                    value={reasoningLon}
                    onChange={(e) => setReasoningLon(e.target.value)}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="reasoning-radius" className="text-xs text-muted-foreground">
                    Radius (km)
                  </Label>
                  <Input
                    id="reasoning-radius"
                    placeholder="10"
                    value={reasoningRadius}
                    onChange={(e) => setReasoningRadius(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="reasoning-context" className="text-xs text-muted-foreground">
                  User / Field Context (Optional, e.g. crop type, land management practices)
                </Label>
                <Input
                  id="reasoning-context"
                  placeholder="e.g. Cropland conversion, intensive tillage, drip irrigation"
                  value={userContextText}
                  onChange={(e) => setUserContextText(e.target.value)}
                />
              </div>

              <div className="flex items-center gap-3 pt-2">
                <Button onClick={handleRunReasoning} disabled={reasoningLoading}>
                  {reasoningLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Synthesizing Multi-Metric Evidence...
                    </>
                  ) : (
                    <>
                      <Layers className="mr-2 h-4 w-4" />
                      Run Multi-Metric Reasoning
                    </>
                  )}
                </Button>
                <span className="text-xs text-muted-foreground">
                  Evaluates NASA POWER, ESA WorldCover, GBIF occurrences, and links to indexed FAO/IPCC literature.
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Reasoning Error */}
          {reasoningError && <ErrorState message={reasoningError} onRetry={handleRunReasoning} />}

          {/* Reasoning Loading */}
          {reasoningLoading && (
            <LoadingState message="Collecting live environmental observations and querying pgvector knowledge layer..." />
          )}

          {/* Reasoning Results */}
          {reasoningResult && !reasoningLoading && (
            <ReasoningResultsSection data={reasoningResult} />
          )}

          {!reasoningResult && !reasoningLoading && !reasoningError && (
            <EmptyState
              icon={<Layers className="h-8 w-8 text-muted-foreground" />}
              title="Awaiting Coordinates"
              description="Enter latitude and longitude or select a preset to trigger multi-metric environmental reasoning."
            />
          )}
        </div>
      )}

      {/* 2. Natural Language Mode */}
      {activeTab === 'natural-language' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Indexed Scientific Literature Search</CardTitle>
              <CardDescription>
                Search indexed FAO and IPCC environmental knowledge base using 384-dimensional vector embeddings.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nl-query">Environmental Inquiry</Label>
                <Textarea
                  id="nl-query"
                  placeholder="e.g. How does soil organic carbon affect water retention and climate resilience in agricultural systems?"
                  value={naturalLanguage}
                  onChange={(e) => setNaturalLanguage(e.target.value)}
                  rows={4}
                  className="resize-none"
                />
              </div>
              <Button onClick={retrieveKnowledge} disabled={!naturalLanguage.trim() || retrievalLoading}>
                <BookOpen className="mr-2 h-4 w-4" />
                {retrievalLoading ? 'Searching Knowledge Base...' : 'Search Scientific Literature'}
              </Button>
            </CardContent>
          </Card>

          {(retrievalError || retrievalResults.length > 0) && (
            <KnowledgeRetrieved results={retrievalResults} error={retrievalError} query={naturalLanguage} />
          )}
        </div>
      )}

      {/* 3. Structured Profile Mode */}
      {activeTab === 'structured' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Manual Observation Input</CardTitle>
              <CardDescription>Legacy manual input form for mock environmental profile assessment.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
                  <MapPin className="h-4 w-4 text-primary" />
                  Location
                </h3>
                <div className="grid gap-4 sm:grid-cols-3">
                  <FieldInput label="Location name" placeholder="Willow Creek Watershed" value={structured.locationName} onChange={(v) => setStructured({ ...structured, locationName: v })} />
                  <FieldInput label="Latitude" placeholder="44.42" value={structured.latitude} onChange={(v) => setStructured({ ...structured, latitude: v })} />
                  <FieldInput label="Longitude" placeholder="-122.65" value={structured.longitude} onChange={(v) => setStructured({ ...structured, longitude: v })} />
                </div>
              </div>
              <div>
                <h3 className="mb-3 text-sm font-semibold text-foreground">Soil</h3>
                <div className="grid gap-4 sm:grid-cols-3">
                  <FieldInput label="pH" placeholder="6.2" value={structured.soilPh} onChange={(v) => setStructured({ ...structured, soilPh: v })} />
                  <FieldInput label="Organic carbon (%)" placeholder="2.8" value={structured.soilOrganicCarbon} onChange={(v) => setStructured({ ...structured, soilOrganicCarbon: v })} />
                  <FieldInput label="Moisture (%)" placeholder="34" value={structured.soilMoisture} onChange={(v) => setStructured({ ...structured, soilMoisture: v })} />
                </div>
              </div>
              <div>
                <h3 className="mb-3 text-sm font-semibold text-foreground">Climate</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  <FieldInput label="Annual rainfall (mm)" placeholder="820" value={structured.annualRainfall} onChange={(v) => setStructured({ ...structured, annualRainfall: v })} />
                  <FieldInput label="Avg temperature (°C)" placeholder="16.5" value={structured.avgTemperature} onChange={(v) => setStructured({ ...structured, avgTemperature: v })} />
                </div>
              </div>
              <div>
                <h3 className="mb-3 text-sm font-semibold text-foreground">Land & Biodiversity</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  <FieldInput label="Land use type" placeholder="Mixed agriculture" value={structured.landUse} onChange={(v) => setStructured({ ...structured, landUse: v })} />
                  <FieldInput label="Species richness" placeholder="72" value={structured.speciesRichness} onChange={(v) => setStructured({ ...structured, speciesRichness: v })} />
                </div>
              </div>
              <Button onClick={handleStructuredSubmit} disabled={structuredLoading}>
                {structuredLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Microscope className="mr-2 h-4 w-4" />}
                Run Assessment
              </Button>
            </CardContent>
          </Card>

          {structuredError && <ErrorState message={structuredError} onRetry={handleStructuredSubmit} />}
          {structuredResult && <AnalysisResults result={structuredResult} />}
        </div>
      )}
    </div>
  );
}

// ==========================================
// CHUNK 4 MULTI-METRIC REASONING COMPONENTS
// ==========================================

function ReasoningResultsSection({ data }: { data: ReasoningResponseDto }) {
  const availableCount = data.availableMetrics?.length || 0;
  const unavailableCount = data.unavailableMetrics?.length || 0;
  const relationships = data.relationships || [];

  return (
    <div className="space-y-6">
      {/* 1. Environmental Context Overview */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-primary" />
              <CardTitle className="text-base">Environmental Data Context</CardTitle>
            </div>
            <span className="text-xs text-muted-foreground">
              {availableCount} Available · {unavailableCount} Unavailable
            </span>
          </div>
          <CardDescription>
            Site coordinates: {data.location?.latitude}°N, {data.location?.longitude}°E (Radius: {data.location?.radiusKm || 10} km)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Available Metrics */}
          <div>
            <h4 className="text-xs font-semibold text-foreground mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
              Available Observations ({availableCount})
            </h4>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {data.availableMetrics?.map((m) => (
                <div key={m.metric} className="rounded-lg border border-border bg-card p-3 shadow-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-muted-foreground capitalize">
                      {m.metric.replace(/_/g, ' ')}
                    </span>
                    <Badge variant="outline" className="text-[10px] bg-emerald-500/10 text-emerald-600 border-emerald-500/20">
                      Live
                    </Badge>
                  </div>
                  <p className="mt-1 text-base font-semibold text-foreground">
                    {String(m.value)} {m.unit || ''}
                  </p>
                  <p className="mt-0.5 text-[10px] text-muted-foreground truncate">
                    {m.source || 'Provider observation'}
                    {m.period ? ` (${m.period})` : ''}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Unavailable Metrics */}
          {unavailableCount > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-foreground mb-2 flex items-center gap-1.5">
                <AlertCircle className="h-3.5 w-3.5 text-amber-500" />
                Unavailable Metrics ({unavailableCount})
              </h4>
              <div className="grid gap-2 sm:grid-cols-2">
                {data.unavailableMetrics?.map((m) => (
                  <div key={m.metric} className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-foreground capitalize">
                        {m.metric.replace(/_/g, ' ')}
                      </span>
                      <Badge variant="outline" className="text-[10px] border-amber-500/30 text-amber-600">
                        {m.availability}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {m.unavailabilityReason || 'Data provider currently offline or unavailable.'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 2. Multi-Metric Environmental Relationships */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" />
              Multi-Metric Environmental Relationships
            </h3>
            <p className="text-xs text-muted-foreground">
              Cross-domain interactions synthesized from ≥3 simultaneous variables and grounded in peer-reviewed science.
            </p>
          </div>
          <Badge variant="secondary" className="text-xs">
            {relationships.length} Detected
          </Badge>
        </div>

        {relationships.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center text-sm text-muted-foreground">
              No cross-domain relationships could be detected with current available metric combinations.
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {relationships.map((rel) => (
              <RelationshipCard key={rel.relationshipId} rel={rel} />
            ))}
          </div>
        )}
      </div>

      {/* 3. Overall Scientific Synthesis */}
      {data.overallInterpretation && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2 text-foreground">
              <Microscope className="h-4 w-4 text-primary" />
              Overall Scientific Synthesis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-foreground">
              {data.overallInterpretation}
            </p>
          </CardContent>
        </Card>
      )}

      {/* 4. Scientific Limitations & Caveats Panel */}
      {data.limitations && data.limitations.length > 0 && (
        <Card className="border-border">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-500" />
              <CardTitle className="text-sm">Scientific Limitations & Data Caveats</CardTitle>
            </div>
            <CardDescription className="text-xs">
              Transparent disclosure of provider downtime, sampling effort constraints, and observational bounds.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-xs text-muted-foreground">
              {data.limitations.map((lim, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-amber-500 font-bold mt-0.5">•</span>
                  <span>{lim}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* 5. Derived Evidence-Backed Recommendations Section */}
      <AnalysisRecommendationsSection reasoningData={data} />
    </div>
  );
}

function AnalysisRecommendationsSection({ reasoningData }: { reasoningData: ReasoningResponseDto }) {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasGenerated, setHasGenerated] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    try {
      const items = await recommendationService.generateRecommendations({
        reasoningResponse: reasoningData,
      });
      setRecs(items);
      setHasGenerated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recommendations.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-3">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-primary" />
              Evidence-Backed Recommendations (Chunk 5)
            </CardTitle>
            <CardDescription className="text-xs">
              Actionable environmental interventions derived directly from the above multi-metric relationships.
            </CardDescription>
          </div>
          <Button
            size="sm"
            onClick={handleGenerate}
            disabled={loading}
            className="self-start sm:self-auto text-xs"
          >
            {loading ? (
              <>
                <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                Deriving Actions...
              </>
            ) : (
              <>
                <Lightbulb className="mr-1.5 h-3.5 w-3.5" />
                {hasGenerated ? 'Re-derive Recommendations' : 'Derive Recommendations'}
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && <p className="text-xs text-destructive mb-3">{error}</p>}
        {hasGenerated && recs.length === 0 && (
          <p className="text-xs text-muted-foreground">No specific actions derived for this metric configuration.</p>
        )}
        {recs.length > 0 && (
          <div className="grid gap-3 sm:grid-cols-2">
            {recs.map((rec) => (
              <RecommendationCard key={rec.id} recommendation={rec} />
            ))}
          </div>
        )}
        {!hasGenerated && (
          <p className="text-xs text-muted-foreground">
            Click 'Derive Recommendations' to generate grounded actions directly from this multi-metric reasoning synthesis without re-querying data providers.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function RelationshipCard({ rel }: { rel: EnvironmentalRelationshipDto }) {
  const [showEvidence, setShowEvidence] = useState(true);

  return (
    <Card className="overflow-hidden border-border transition-all">
      <CardHeader className="pb-3 bg-muted/20">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <h4 className="text-sm font-bold text-foreground">{rel.title}</h4>
              {rel.isMultiMetric ? (
                <Badge className="bg-primary/10 text-primary border-primary/20 text-[11px] font-semibold">
                  {rel.metricsCount}-Metric Synthesis
                </Badge>
              ) : (
                <Badge variant="outline" className="border-amber-500/30 text-amber-600 text-[11px]">
                  {rel.fallbackLabel || 'Limited 2-Metric Analysis'}
                </Badge>
              )}
              {rel.evidenceStatus === 'supported' ? (
                <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-500/20 text-[10px]">
                  Evidence Supported
                </Badge>
              ) : (
                <Badge variant="outline" className="bg-muted text-muted-foreground text-[10px]">
                  Insufficient Evidence
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-1 mt-1">
              {rel.metrics.map((m) => (
                <Badge key={m} variant="secondary" className="text-[10px] font-mono">
                  {m}
                </Badge>
              ))}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="text-xs h-7 self-start sm:self-auto"
            onClick={() => setShowEvidence(!showEvidence)}
          >
            <BookOpen className="mr-1.5 h-3.5 w-3.5 text-primary" />
            {showEvidence ? 'Hide Evidence' : `View Evidence (${rel.evidence.length})`}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        <p className="text-sm leading-relaxed text-foreground">
          {rel.interpretation}
        </p>

        {/* Linked Evidence */}
        {showEvidence && rel.evidence && rel.evidence.length > 0 && (
          <div className="space-y-2 pt-2 border-t border-border">
            <h5 className="text-xs font-semibold text-foreground flex items-center gap-1.5">
              <BookOpen className="h-3.5 w-3.5 text-primary" />
              Authoritative Peer-Reviewed Evidence (pgvector)
            </h5>
            <div className="grid gap-3 sm:grid-cols-1">
              {rel.evidence.map((ev) => (
                <div key={ev.chunkId} className="rounded-lg border border-border/80 bg-card p-3 shadow-2xs">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs font-semibold text-foreground">{ev.title}</p>
                      <p className="text-[11px] text-muted-foreground">
                        {ev.organization} {ev.publicationYear ? `(${ev.publicationYear})` : ''} · Source: {ev.source}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-[10px] shrink-0 font-mono">
                      {Math.round(ev.retrievalScore * 100)}% match
                    </Badge>
                  </div>
                  <blockquote className="mt-2 border-l-2 border-primary/40 pl-2 text-xs italic text-muted-foreground leading-relaxed">
                    "{ev.excerpt}"
                  </blockquote>
                  {ev.sourceUrl && (
                    <a
                      href={ev.sourceUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex items-center gap-1 text-[11px] text-primary hover:underline"
                    >
                      <ExternalLink className="h-3 w-3" />
                      View authoritative publication
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Relationship limitations */}
        {rel.limitations && rel.limitations.length > 0 && (
          <div className="rounded-md bg-muted/40 p-2.5 text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Scientific note: </span>
            {rel.limitations.join(' ')}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ==========================================
// PRE-EXISTING RETRIEVAL & MOCK COMPONENTS
// ==========================================

function KnowledgeRetrieved({ results, error, query }: { results: KnowledgeSearchResult[]; error: string; query: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Knowledge retrieved</CardTitle>
        <CardDescription>Evidence retrieved from the indexed knowledge layer. This is not an AI-generated answer.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">Query: <span className="text-foreground">{query}</span></p>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {results.map((item) => (
          <div key={item.chunkId} className="rounded-lg border border-border p-3">
            <div className="flex items-start justify-between gap-3">
              <div><p className="text-sm font-medium text-foreground">{item.title}</p><p className="text-xs text-muted-foreground">{item.organization} {item.year || ''}</p></div>
              <span className="text-xs text-muted-foreground">{Math.round(item.relevanceScore * 100)}% match</span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-muted-foreground">{item.text}</p>
            <div className="mt-2 flex flex-wrap gap-1">{item.matchedMetrics.map((metric) => <Badge key={metric} variant="secondary" className="text-[10px]">{metric}</Badge>)}</div>
            <a className="mt-2 inline-block text-xs font-medium text-primary hover:underline" href={item.sourceUrl} target="_blank" rel="noreferrer">View source</a>
          </div>
        ))}
        {!error && results.length === 0 && <p className="text-sm text-muted-foreground">No indexed evidence matched this query.</p>}
      </CardContent>
    </Card>
  );
}

function FieldInput({
  label,
  placeholder,
  value,
  onChange,
}: {
  label: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="space-y-1.5">
      <Label className="text-xs text-muted-foreground">{label}</Label>
      <Input placeholder={placeholder} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

function AnalysisResults({ result }: { result: AnalysisResult }) {
  return (
    <div className="space-y-6 animate-in">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                <Microscope className="h-4 w-4 text-primary" />
              </div>
              <CardTitle>Environmental Assessment</CardTitle>
            </div>
            <ConfidenceBadge level={result.confidence} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
            <HealthScoreRing score={result.overallHealthScore} size={120} />
            <div className="flex-1">
              <p className="text-sm leading-relaxed text-foreground">{result.assessmentSummary}</p>
              <div className="mt-4 flex items-center gap-4 text-sm">
                <span className="text-muted-foreground">Confidence score:</span>
                <span className="font-medium text-foreground">{result.confidenceScore}%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
