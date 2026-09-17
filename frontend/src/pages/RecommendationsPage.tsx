import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Lightbulb, Filter, ArrowRight, Sparkles, Loader2, MapPin } from 'lucide-react';
import type { Recommendation } from '@/models';
import { recommendationService } from '@/services';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { RecommendationCard } from '@/components/shared/RecommendationCard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

type FilterStatus = 'all' | Recommendation['status'];

const statusFilters: { value: FilterStatus; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'suggested', label: 'Suggested' },
  { value: 'in-progress', label: 'In Progress' },
  { value: 'implemented', label: 'Implemented' },
  { value: 'dismissed', label: 'Dismissed' },
];

const statusColors: Record<Recommendation['status'], string> = {
  suggested: 'bg-chart-3/10 text-chart-3',
  'in-progress': 'bg-warning/10 text-warning',
  implemented: 'bg-success/10 text-success',
  dismissed: 'bg-muted text-muted-foreground',
};

export function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<FilterStatus>('all');

  // Generator state
  const [genLat, setGenLat] = useState('19.0760');
  const [genLon, setGenLon] = useState('72.8777');
  const [genLoading, setGenLoading] = useState(false);
  const [genError, setGenError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    recommendationService
      .getRecommendations()
      .then(setRecommendations)
      .catch(() => setError('Failed to load recommendations.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleGenerate = async () => {
    const lat = parseFloat(genLat);
    const lon = parseFloat(genLon);
    if (isNaN(lat) || isNaN(lon)) {
      setGenError('Please enter valid coordinates.');
      return;
    }
    setGenLoading(true);
    setGenError('');
    try {
      const items = await recommendationService.generateRecommendations({
        latitude: lat,
        longitude: lon,
      });
      setRecommendations(items);
    } catch (err) {
      setGenError(err instanceof Error ? err.message : 'Failed to generate recommendations.');
    } finally {
      setGenLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading recommendations..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const filtered =
    filter === 'all' ? recommendations : recommendations.filter((r) => r.status === filter);

  return (
    <div className="space-y-6 animate-in">
      <PageHeader
        title="Recommendations"
        description="Evidence-backed environmental actions derived directly from multi-metric scientific reasoning."
      />

      {/* Direct Generator Card */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <CardTitle className="text-sm font-semibold">Generate Recommendations from Location Reasoning</CardTitle>
            </div>
            <div className="flex gap-1.5">
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => { setGenLat('19.0760'); setGenLon('72.8777'); }}
              >
                Mumbai
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => { setGenLat('19.8000'); setGenLon('74.4000'); }}
              >
                Nashik Cropland
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => { setGenLat('-1.2921'); setGenLon('36.8219'); }}
              >
                Nairobi
              </Button>
            </div>
          </div>
          <CardDescription className="text-xs">
            Synthesizes multi-metric observations, evaluates cross-domain interactions, and derives grounded interventions backed by FAO and IPCC literature.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end gap-3">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Latitude</Label>
              <Input
                className="h-8 w-28 text-xs"
                value={genLat}
                onChange={(e) => setGenLat(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Longitude</Label>
              <Input
                className="h-8 w-28 text-xs"
                value={genLon}
                onChange={(e) => setGenLon(e.target.value)}
              />
            </div>
            <Button
              size="sm"
              className="h-8 text-xs"
              onClick={handleGenerate}
              disabled={genLoading}
            >
              {genLoading ? (
                <>
                  <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-1.5 h-3.5 w-3.5" />
                  Generate for Coordinates
                </>
              )}
            </Button>
          </div>
          {genError && <p className="mt-2 text-xs text-destructive">{genError}</p>}
        </CardContent>
      </Card>

      {/* Status filter */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Filter className="h-4 w-4" />
          Filter:
        </span>
        {statusFilters.map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={cn(
              'rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors',
              filter === f.value
                ? 'border-primary bg-primary/5 text-primary'
                : 'border-border text-muted-foreground hover:text-foreground',
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={<Lightbulb className="h-7 w-7 text-muted-foreground" />}
          title="No recommendations found"
          description="Click 'Generate for Coordinates' above or run a multi-metric analysis to produce evidence-backed recommendations."
          action={
            <Button size="sm" asChild>
              <Link to="/analysis">
                Run analysis
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((rec) => (
            <div key={rec.id} className="relative">
              <RecommendationCard recommendation={rec} />
              <div className="absolute right-3 top-3">
                <span
                  className={cn(
                    'rounded-md px-2 py-0.5 text-[10px] font-semibold capitalize',
                    statusColors[rec.status],
                  )}
                >
                  {rec.status.replace('-', ' ')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
