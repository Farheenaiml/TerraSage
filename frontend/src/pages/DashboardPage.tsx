import { useEffect, useState } from 'react';
import { Beaker, Globe, Leaf, Sprout, ShieldAlert, Microscope, Database } from 'lucide-react';
import type { DashboardData } from '@/models';
import { dashboardService } from '@/services';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    dashboardService.getDashboard().then(setData).catch(() => setError('Failed to load dashboard data.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) return <LoadingState message="Loading environmental overview..." />;
  if (error || !data) return <ErrorState message={error || 'No data available.'} onRetry={load} />;

  const profile = data.profile;
  return (
    <div className="space-y-6 animate-in">
      <PageHeader title="Dashboard" description={profile?.locationName ? `Environmental overview for ${profile.locationName}.` : 'Environmental overview.'} />
      <div className="grid gap-4 sm:grid-cols-2">
        <AvailabilityCard label="Environmental factors available" value={data.availableFields.length} />
        <AvailabilityCard label="Environmental factors missing" value={data.missingFields.length} muted />
      </div>
      {!profile ? (
        <Card><CardContent><EmptyState title="No environmental profile available yet." description="Add environmental data to begin." /></CardContent></Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
          <MetricCard icon={Beaker} title="Soil" values={[["pH", profile.soil.ph], ["Organic Carbon", profile.soil.organicCarbonPercent, "%"], ["Moisture", profile.soil.moisturePercent, "%"]]} />
          <MetricCard icon={Globe} title="Climate" values={[["Temperature", profile.climate.avgTemperatureC, "°C"], ["Rainfall", profile.climate.annualRainfallMm, " mm"]]} />
          <MetricCard icon={Leaf} title="Land" values={[["Land Use", profile.land.landUseType], ["Land Cover", profile.land.coverType]]} />
          <MetricCard icon={Sprout} title="Biodiversity" values={[["Species Richness", profile.biodiversity.speciesRichness], ["Habitat Diversity", profile.biodiversity.habitatDiversityIndex]]} />
          <MetricCard icon={ShieldAlert} title="Human Impact" values={[["Pollution", profile.humanImpact.pollutionIndex], ["Deforestation", profile.humanImpact.deforestationRatePercent, "%"]]} />
        </div>
      )}
      <div className="grid gap-4 lg:grid-cols-3">
        <PlaceholderCard title="Recent analyses" icon={Microscope} message="No analyses available yet." />
        <PlaceholderCard title="Recommendations" icon={Leaf} message="Recommendations will appear after analysis." />
        <PlaceholderCard title="Evidence" icon={Database} message={data.evidenceSummary.total > 0 ? `${data.evidenceSummary.total} indexed evidence sources.` : 'No evidence sources indexed yet.'} />
      </div>
    </div>
  );
}

function AvailabilityCard({ label, value, muted = false }: { label: string; value: number; muted?: boolean }) {
  return <Card><CardContent className="flex items-center gap-4 p-5"><div className={`flex h-11 w-11 items-center justify-center rounded-lg ${muted ? 'bg-muted' : 'bg-primary/10'}`}><Database className={`h-5 w-5 ${muted ? 'text-muted-foreground' : 'text-primary'}`} /></div><div><p className="font-display text-2xl font-bold text-foreground">{value}</p><p className="text-xs text-muted-foreground">{label}</p></div></CardContent></Card>;
}

function MetricCard({ icon: Icon, title, values }: { icon: React.ComponentType<{ className?: string }>; title: string; values: [string, number | string | null | undefined, string?][] }) {
  return <Card><CardHeader className="pb-3"><div className="flex items-center gap-2"><Icon className="h-4 w-4 text-primary" /><CardTitle className="text-base">{title}</CardTitle></div></CardHeader><CardContent className="space-y-3 pt-0">{values.map(([label, value, unit]) => <MetricRow key={label} label={label} value={value == null || value === '' ? '—' : `${value}${unit || ''}`} />)}</CardContent></Card>;
}

function PlaceholderCard({ title, icon: Icon, message }: { title: string; icon: React.ComponentType<{ className?: string }>; message: string }) {
  return <Card><CardHeader className="pb-0"><div className="flex items-center gap-2"><Icon className="h-4 w-4 text-primary" /><CardTitle className="text-base">{title}</CardTitle></div></CardHeader><CardContent><p className="py-5 text-sm text-muted-foreground">{message}</p></CardContent></Card>;
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return <div className="flex items-center justify-between"><span className="text-sm text-muted-foreground">{label}</span><span className="text-sm font-medium text-foreground">{value}</span></div>;
}
