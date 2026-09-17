import { useEffect, useState, useMemo } from 'react';
import { Search, BookOpen, X, Sparkles } from 'lucide-react';
import type { EvidenceReference, EvidenceType } from '@/models';
import { evidenceService } from '@/services';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { EvidenceCard } from '@/components/shared/EvidenceCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

const typeOptions: { value: EvidenceType | 'all'; label: string }[] = [
  { value: 'all', label: 'All types' },
  { value: 'peer-reviewed', label: 'Peer-Reviewed' },
  { value: 'meta-analysis', label: 'Meta-Analysis' },
  { value: 'government-report', label: 'Government Report' },
  { value: 'ngo-report', label: 'NGO Report' },
  { value: 'dataset', label: 'Dataset' },
  { value: 'guideline', label: 'Guideline' },
];

export function EvidencePage() {
  const [allEvidence, setAllEvidence] = useState<EvidenceReference[]>([]);
  const [filtered, setFiltered] = useState<EvidenceReference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<EvidenceType | 'all'>('all');

  const load = () => {
    setLoading(true);
    setError('');
    evidenceService
      .getEvidence()
      .then((data) => {
        setAllEvidence(data);
        setFiltered(data);
      })
      .catch(() => setError('Failed to load evidence library.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    const q = query.trim().toLowerCase();

    // 1. Instant local search across indexed sources
    let localMatches = allEvidence;
    if (q) {
      localMatches = allEvidence.filter((item) => {
        const titleMatch = (item.title || '').toLowerCase().includes(q);
        const summaryMatch = (item.summary || '').toLowerCase().includes(q);
        const orgMatch = (item.organization || '').toLowerCase().includes(q);
        const metricMatch = (item.metrics || []).some((m) => m.toLowerCase().includes(q));
        return titleMatch || summaryMatch || orgMatch || metricMatch;
      });
    }

    if (typeFilter !== 'all') {
      localMatches = localMatches.filter((item) => item.type === typeFilter);
    }

    setFiltered(localMatches);

    // 2. Concurrently query server-side deep RAG index if query is provided
    if (q) {
      evidenceService
        .getEvidence({ query: q })
        .then((remoteResults) => {
          if (remoteResults && remoteResults.length > 0) {
            const remoteFiltered =
              typeFilter === 'all'
                ? remoteResults
                : remoteResults.filter((item) => item.type === typeFilter);

            // Merge local and remote results without duplicates by id/title
            const seen = new Set<string>();
            const combined: EvidenceReference[] = [];

            for (const item of [...remoteFiltered, ...localMatches]) {
              const key = (item.title || '') + (item.id || '');
              if (!seen.has(key)) {
                seen.add(key);
                combined.push(item);
              }
            }

            if (combined.length > 0) {
              setFiltered(combined);
            }
          }
        })
        .catch((err) => {
          console.warn('Remote knowledge search error, kept local matches:', err);
        });
    }
  }, [query, typeFilter, allEvidence]);

  const organizations = useMemo(() => {
    const orgs = new Set(allEvidence.map((e) => e.organization));
    return Array.from(orgs).sort();
  }, [allEvidence]);

  if (loading) return <LoadingState message="Loading evidence library..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-6 animate-in">
      <PageHeader
        title="Evidence Library"
        description="Searchable scientific evidence sources backing TerraSage analyses and recommendations."
      />

      {/* Search + filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by title, summary, organization, or metric (e.g. soil, carbon, biodiversity, FAO)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10 pr-10"
              />
              {query && (
                <button
                  onClick={() => setQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Suggested quick searches */}
            <div className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
              <span className="flex items-center gap-1 font-medium text-foreground">
                <Sparkles className="h-3 w-3 text-primary" /> Popular Topics:
              </span>
              {['Soil Organic Carbon', 'Biodiversity', 'Agroforestry', 'Conservation Agriculture', 'IPCC'].map(
                (topic) => (
                  <button
                    key={topic}
                    onClick={() => setQuery(topic)}
                    className="rounded-full bg-muted/60 hover:bg-muted px-2.5 py-0.5 text-xs text-muted-foreground transition-colors hover:text-foreground border border-border/50"
                  >
                    {topic}
                  </button>
                )
              )}
            </div>

            <div className="flex flex-wrap gap-2">
              {typeOptions.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setTypeFilter(opt.value)}
                  className={cn(
                    'rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors',
                    typeFilter === opt.value
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-border text-muted-foreground hover:text-foreground',
                  )}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            {organizations.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                <span className="font-medium">Organizations:</span>
                {organizations.map((org) => (
                  <span key={org} className="rounded bg-muted px-1.5 py-0.5">
                    {org}
                  </span>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {filtered.length} {filtered.length === 1 ? 'source' : 'sources'} found
        </p>
      </div>

      {/* Evidence grid */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={<BookOpen className="h-7 w-7 text-muted-foreground" />}
          title={allEvidence.length === 0 ? 'No evidence sources indexed yet.' : 'No evidence found'}
          description={
            allEvidence.length === 0
              ? 'Index an authoritative source to begin.'
              : `No sources matched "${query}". Try searching for 'soil', 'biodiversity', or 'FAO'.`
          }
          action={
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setQuery('');
                setTypeFilter('all');
              }}
            >
              Clear filters
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((ev) => (
            <EvidenceCard key={ev.id} evidence={ev} />
          ))}
        </div>
      )}
    </div>
  );
}
