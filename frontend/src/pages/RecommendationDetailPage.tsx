import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  Target,
  TrendingUp,
  BookOpen,
  Lightbulb,
  CheckCircle2,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import type { Recommendation } from '@/models';
import { recommendationService } from '@/services';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { ConfidenceBadge, TimeHorizonBadge, PriorityBadge } from '@/components/shared/Badges';
import { EvidenceCard } from '@/components/shared/EvidenceCard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const statusOptions: { value: Recommendation['status']; label: string }[] = [
  { value: 'suggested', label: 'Suggested' },
  { value: 'in-progress', label: 'In Progress' },
  { value: 'implemented', label: 'Implemented' },
  { value: 'dismissed', label: 'Dismissed' },
];

export function RecommendationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    if (!id) return;
    recommendationService
      .getRecommendation(id)
      .then(setRec)
      .catch(() => setError('Failed to load recommendation.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  const updateStatus = async (status: Recommendation['status']) => {
    if (!id) return;
    try {
      const updated = await recommendationService.updateStatus(id, status);
      setRec(updated);
    } catch {
      // ignore error in update
    }
  };

  if (loading) return <LoadingState message="Loading recommendation..." />;
  if (error || !rec) return <ErrorState message={error || 'Recommendation not found.'} onRetry={load} />;

  return (
    <div className="space-y-6 animate-in">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild className="h-8 w-8">
          <Link to="/recommendations">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="font-display text-2xl font-bold text-foreground">{rec.title}</h1>
          <p className="mt-1 text-sm text-muted-foreground capitalize">{rec.category.replace(/_/g, ' ')}</p>
        </div>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap items-center gap-2">
        <PriorityBadge priority={rec.priority} />
        <TimeHorizonBadge horizon={rec.timeHorizon} />
        <ConfidenceBadge level={rec.confidence} />
        {rec.confidenceScore !== null && rec.confidenceScore !== undefined ? (
          <Badge variant="outline" className="text-xs">
            {rec.confidenceScore}% confidence
          </Badge>
        ) : (
          <Badge variant="outline" className="text-xs capitalize flex items-center gap-1">
            <ShieldCheck className="h-3 w-3 text-primary" />
            Qualitative evidence grounding
          </Badge>
        )}
      </div>

      {/* What to do */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <Target className="h-4 w-4 text-primary" />
            </div>
            <CardTitle className="text-base">What to do</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed text-foreground">{rec.description}</p>
        </CardContent>
      </Card>

      {/* Why it works */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-chart-3/10">
              <Lightbulb className="h-4 w-4 text-chart-3" />
            </div>
            <CardTitle className="text-base">Scientific Rationale & Context</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm leading-relaxed text-foreground">{rec.rationale}</p>
          {rec.confidenceRationale && (
            <div className="rounded-md bg-muted/40 p-3 text-xs text-muted-foreground border border-border">
              <span className="font-semibold text-foreground">Confidence basis: </span>
              {rec.confidenceRationale}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Impacted metrics + Expected impact */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-success/10">
                <TrendingUp className="h-4 w-4 text-success" />
              </div>
              <CardTitle className="text-base">Impacted Metrics</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {rec.impactedMetrics.map((m) => (
                <span
                  key={m}
                  className="rounded-md bg-primary/5 px-2.5 py-1 text-xs font-mono font-medium text-primary"
                >
                  {m}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
                <Clock className="h-4 w-4 text-accent-foreground" />
              </div>
              <CardTitle className="text-base">Expected Scientific Impact</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-foreground">{rec.expectedImpact}</p>
            <p className="mt-2 text-xs text-muted-foreground">
              Time horizon: {rec.timeHorizon.replace('-', ' ')}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Limitations / Site Caveats */}
      {rec.limitations && rec.limitations.length > 0 && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-500" />
              <CardTitle className="text-sm">Mandatory Scientific Limitations & Caveats</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1 text-xs text-muted-foreground">
              {rec.limitations.map((lim, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{lim}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Evidence */}
      {rec.evidence && rec.evidence.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-chart-3/10">
                <BookOpen className="h-4 w-4 text-chart-3" />
              </div>
              <div>
                <CardTitle className="text-base">Authoritative Scientific Evidence</CardTitle>
                <CardDescription>Directly inherited peer-reviewed chunks from pgvector</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              {rec.evidence.map((ev) => (
                <EvidenceCard key={ev.id} evidence={ev} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Status update */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <CheckCircle2 className="h-4 w-4 text-primary" />
            </div>
            <CardTitle className="text-base">Lifecycle Status</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {statusOptions.map((opt) => (
              <Button
                key={opt.value}
                variant={rec.status === opt.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => updateStatus(opt.value)}
              >
                {opt.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
