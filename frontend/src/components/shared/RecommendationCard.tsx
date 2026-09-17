import { Link } from 'react-router-dom';
import { ArrowRight, TrendingUp, TrendingDown, Minus, Clock, ShieldCheck } from 'lucide-react';
import type { Recommendation } from '@/models';
import { Card, CardContent } from '@/components/ui/card';
import { ConfidenceBadge, TimeHorizonBadge, PriorityBadge } from './Badges';
import { cn } from '@/lib/utils';

interface RecommendationCardProps {
  recommendation: Recommendation;
  className?: string;
}

export function RecommendationCard({ recommendation, className }: RecommendationCardProps) {
  const rec = recommendation;
  return (
    <Link to={`/recommendations/${rec.id}`} className="block h-full">
      <Card className={cn('h-full transition-all hover:shadow-md hover:border-primary/30', className)}>
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-3">
            <div className="flex flex-wrap gap-1.5">
              <PriorityBadge priority={rec.priority} />
              <TimeHorizonBadge horizon={rec.timeHorizon} />
            </div>
            <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground" />
          </div>
          <h3 className="mt-3 font-display text-base font-semibold leading-snug text-foreground">
            {rec.title}
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground line-clamp-2">
            {rec.description}
          </p>
          <div className="mt-4 flex flex-wrap gap-1.5">
            {rec.impactedMetrics.slice(0, 3).map((m) => (
              <span
                key={m}
                className="rounded-md bg-primary/5 px-2 py-0.5 text-xs font-medium text-primary"
              >
                {m}
              </span>
            ))}
            {rec.impactedMetrics.length > 3 && (
              <span className="text-xs text-muted-foreground">
                +{rec.impactedMetrics.length - 3} more
              </span>
            )}
          </div>
          <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
            <ConfidenceBadge level={rec.confidence} />
            {rec.confidenceScore !== null && rec.confidenceScore !== undefined ? (
              <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {rec.confidenceScore}% confidence
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground capitalize font-medium">
                <ShieldCheck className="h-3.5 w-3.5 text-primary/70" />
                {rec.confidence} evidence
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export function MetricChangeIndicator({
  direction,
  className,
}: {
  direction: 'increase' | 'decrease' | 'stabilize';
  className?: string;
}) {
  const Icon =
    direction === 'increase' ? TrendingUp : direction === 'decrease' ? TrendingDown : Minus;
  const color =
    direction === 'increase'
      ? 'text-success'
      : direction === 'decrease'
        ? 'text-destructive'
        : 'text-muted-foreground';
  return <Icon className={cn('h-4 w-4', color, className)} />;
}
