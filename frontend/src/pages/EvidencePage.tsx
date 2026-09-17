import { useEffect, useState, useMemo } from 'react';
import { Search, BookOpen, X } from 'lucide-react';
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
    if (query.trim()) {
      evidenceService.getEvidence({ query }).then((results) => {
        setFiltered(typeFilter === 'all' ? results : results.filter((item) => item.type === typeFilter));
      }).catch(() => setError('Knowledge search is unavailable.'));
      return;
    }
    let results = allEvidence;
    if (typeFilter !== 'all') {
      results = results.filter((e) => e.type === typeFilter);
    }
    setFiltered(results);
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
                placeholder="Search by title, summary, organization, or metric..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-10"
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
          description={allEvidence.length === 0 ? 'Index an authoritative source to begin.' : 'Try adjusting your search query or filters.'}
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
