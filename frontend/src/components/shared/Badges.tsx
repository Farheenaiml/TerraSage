import { cn } from '@/lib/utils';
import type { ConfidenceLevel, TimeHorizon } from '@/models';
import { Badge } from '@/components/ui/badge';

const confidenceConfig: Record<ConfidenceLevel, { label: string; className: string }> = {
  high: { label: 'High Confidence', className: 'bg-success/10 text-success border-success/20' },
  medium: { label: 'Medium Confidence', className: 'bg-warning/10 text-warning border-warning/20' },
  low: { label: 'Low Confidence', className: 'bg-destructive/10 text-destructive border-destructive/20' },
};

export function ConfidenceBadge({ level, className }: { level: ConfidenceLevel; className?: string }) {
  const config = confidenceConfig[level];
  return (
    <Badge variant="outline" className={cn(config.className, 'font-medium', className)}>
      {config.label}
    </Badge>
  );
}

const horizonConfig: Record<TimeHorizon, { label: string; className: string }> = {
  'short-term': { label: 'Short-term', className: 'bg-chart-3/10 text-chart-3 border-chart-3/20' },
  'medium-term': { label: 'Medium-term', className: 'bg-chart-2/10 text-chart-2 border-chart-2/20' },
  'long-term': { label: 'Long-term', className: 'bg-chart-1/10 text-chart-1 border-chart-1/20' },
};

export function TimeHorizonBadge({ horizon, className }: { horizon: TimeHorizon; className?: string }) {
  const config = horizonConfig[horizon];
  return (
    <Badge variant="outline" className={cn(config.className, 'font-medium', className)}>
      {config.label}
    </Badge>
  );
}

const priorityConfig: Record<'high' | 'medium' | 'low', { label: string; className: string }> = {
  high: { label: 'High Priority', className: 'bg-destructive/10 text-destructive border-destructive/20' },
  medium: { label: 'Medium Priority', className: 'bg-warning/10 text-warning border-warning/20' },
  low: { label: 'Low Priority', className: 'bg-muted text-muted-foreground border-border' },
};

export function PriorityBadge({ priority, className }: { priority: 'high' | 'medium' | 'low'; className?: string }) {
  const config = priorityConfig[priority];
  return (
    <Badge variant="outline" className={cn(config.className, 'font-medium', className)}>
      {config.label}
    </Badge>
  );
}

const statusConfig: Record<
  'optimal' | 'adequate' | 'suboptimal' | 'critical' | 'unknown',
  { label: string; dotClass: string; textClass: string }
> = {
  optimal: { label: 'Optimal', dotClass: 'bg-success', textClass: 'text-success' },
  adequate: { label: 'Adequate', dotClass: 'bg-chart-4', textClass: 'text-chart-4' },
  suboptimal: { label: 'Suboptimal', dotClass: 'bg-warning', textClass: 'text-warning' },
  critical: { label: 'Critical', dotClass: 'bg-destructive', textClass: 'text-destructive' },
  unknown: { label: 'Unknown', dotClass: 'bg-muted-foreground', textClass: 'text-muted-foreground' },
};

export function StatusIndicator({
  status,
  showLabel = true,
  className,
}: {
  status: 'optimal' | 'adequate' | 'suboptimal' | 'critical' | 'unknown';
  showLabel?: boolean;
  className?: string;
}) {
  const config = statusConfig[status];
  return (
    <span className={cn('inline-flex items-center gap-2', className)}>
      <span className={cn('h-2 w-2 rounded-full', config.dotClass)} />
      {showLabel && <span className={cn('text-xs font-medium', config.textClass)}>{config.label}</span>}
    </span>
  );
}
