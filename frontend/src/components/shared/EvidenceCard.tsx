import { FileText, ExternalLink, Building2, Calendar } from 'lucide-react';
import type { EvidenceReference } from '@/models';
import { evidenceTypeLabels } from '@/data/evidence';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface EvidenceCardProps {
  evidence: EvidenceReference;
  compact?: boolean;
  className?: string;
}

export function EvidenceCard({ evidence, compact, className }: EvidenceCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-card p-4 transition-shadow hover:shadow-md',
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/5">
            <FileText className="h-4 w-4 text-primary" />
          </div>
          <Badge variant="outline" className="text-xs font-medium">
            {evidenceTypeLabels[evidence.type] || evidence.type}
          </Badge>
        </div>
        {evidence.relevanceScore !== undefined && (
          <span className="text-xs font-medium text-muted-foreground">
            {Math.round(evidence.relevanceScore * 100)}% match
          </span>
        )}
      </div>
      <h4 className="mt-3 text-sm font-semibold leading-snug text-foreground">
        {evidence.title}
      </h4>
      {!compact && (
        <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground line-clamp-2">
          {evidence.summary}
        </p>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1">
          <Building2 className="h-3 w-3" />
          {evidence.organization}
        </span>
        <span className="inline-flex items-center gap-1">
          <Calendar className="h-3 w-3" />
          {evidence.year}
        </span>
        <span className="truncate">{evidence.source}</span>
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
        {evidence.metrics.slice(0, 4).map((m) => (
          <span key={m} className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            {m}
          </span>
        ))}
      </div>
      <a
        href={evidence.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
      >
        View source
        <ExternalLink className="h-3 w-3" />
      </a>
    </div>
  );
}
