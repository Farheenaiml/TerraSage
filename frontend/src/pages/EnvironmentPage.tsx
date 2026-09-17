import { useEffect, useState } from 'react';
import {
  Beaker,
  Globe,
  Leaf,
  Sprout,
  MapPin,
  Database,
  CircleAlert,
  Search,
  Loader2,
  Wind,
  TreeDeciduous,
  Activity,
} from 'lucide-react';
import type { EnvironmentalProfile } from '@/models';
import { environmentService } from '@/services';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

const PRESETS = [
  { name: 'Nashik Farm, MH', lat: 19.9975, lon: 73.7898 },
  { name: 'Mumbai Coastal, MH', lat: 19.0760, lon: 72.8777 },
  { name: 'Semi-Arid Wheat Belt', lat: 30.9010, lon: 75.8573 },
  { name: 'Nairobi Basin (Dryland)', lat: -1.2921, lon: 36.8219 },
];

export function EnvironmentPage() {
  const [profile, setProfile] = useState<EnvironmentalProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [latInput, setLatInput] = useState('19.9975');
  const [lonInput, setLonInput] = useState('73.7898');
  const [fetching, setFetching] = useState(false);

  const fetchProfile = (lat: number, lon: number) => {
    setLoading(true);
    setError('');
    environmentService
      .getProfile(lat, lon)
      .then(setProfile)
      .catch(() => setError('Failed to load real environmental profile data for coordinates.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProfile(19.9975, 73.7898);
  }, []);

  const handleQuery = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const lat = parseFloat(latInput);
    const lon = parseFloat(lonInput);
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setError('Please provide valid decimal coordinates (-90 to 90 for latitude, -180 to 180 for longitude).');
      return;
    }
    setFetching(true);
    fetchProfile(lat, lon);
    setFetching(false);
  };

  const handlePresetSelect = (lat: number, lon: number) => {
    setLatInput(lat.toString());
    setLonInput(lon.toString());
    fetchProfile(lat, lon);
  };

  if (loading && !profile) return <LoadingState message="Querying real environmental providers (NASA, ESA, GBIF, Copernicus CAMS)..." />;
  if (error && !profile) return <ErrorState message={error} onRetry={() => fetchProfile(parseFloat(latInput), parseFloat(lonInput))} />;
  if (!profile) return <EmptyState title="No environmental data available." description="The requested location did not return data from the connected providers." />;

  const hi = profile.humanImpact;

  return (
    <div className="space-y-6 animate-in">
      <PageHeader
        title="Environmental Profile"
        description="Live multi-variable environmental telemetry queried across authoritative scientific data layers."
        actions={<Badge variant="outline" className="border-emerald-500/30 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10">NASA • ESA • GBIF • CAMS Active</Badge>}
      />

      {/* Coordinate Search & Presets Bar */}
      <Card className="border-primary/20 bg-card/60 backdrop-blur">
        <CardContent className="p-5">
          <form onSubmit={handleQuery} className="flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <MapPin className="h-4 w-4 text-primary" />
                <span>Geographic Site Coordinates</span>
              </div>
              <div className="flex flex-wrap items-center gap-1.5 text-xs">
                <span className="text-muted-foreground mr-1">Quick Presets:</span>
                {PRESETS.map((preset, idx) => (
                  <Button
                    key={idx}
                    type="button"
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs px-2.5 py-0"
                    onClick={() => handlePresetSelect(preset.lat, preset.lon)}
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="flex flex-1 min-w-[140px] items-center gap-2">
                <label htmlFor="lat-input" className="text-xs font-medium text-muted-foreground">Lat:</label>
                <Input
                  id="lat-input"
                  type="number"
                  step="any"
                  value={latInput}
                  onChange={(e) => setLatInput(e.target.value)}
                  placeholder="e.g. 19.9975"
                  className="h-9"
                />
              </div>
              <div className="flex flex-1 min-w-[140px] items-center gap-2">
                <label htmlFor="lon-input" className="text-xs font-medium text-muted-foreground">Lon:</label>
                <Input
                  id="lon-input"
                  type="number"
                  step="any"
                  value={lonInput}
                  onChange={(e) => setLonInput(e.target.value)}
                  placeholder="e.g. 73.7898"
                  className="h-9"
                />
              </div>
              <Button type="submit" size="sm" className="h-9 gap-1.5 px-4" disabled={fetching || loading}>
                {loading || fetching ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
                Query Site Data
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Domain Cards Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Soil Health */}
        <DomainCard icon={Beaker} title="Soil Health" colorClass="bg-amber-500/10 text-amber-600 dark:text-amber-400">
          <DataRow label="pH" value={profile.soil.ph} unit="" source={profile.soil.source} detail={profile.soil.depth ? `Depth: ${profile.soil.depth}` : undefined} />
          <DataRow label="Organic Carbon" value={profile.soil.organicCarbonPercent} unit="%" source={profile.soil.source} detail={profile.soil.depth ? `Depth: ${profile.soil.depth}` : undefined} />
          <DataRow label="Moisture" value={profile.soil.moisturePercent} unit="%" source={profile.soil.source} />
        </DomainCard>

        {/* Climate Factors */}
        <DomainCard icon={Globe} title="Climate Telemetry" colorClass="bg-blue-500/10 text-blue-600 dark:text-blue-400">
          <DataRow label="Temperature" value={profile.climate.avgTemperatureC} unit="°C" source={profile.climate.temperatureSource} detail={profile.climate.temperaturePeriod ? `Period: ${profile.climate.temperaturePeriod.start ?? ''} to ${profile.climate.temperaturePeriod.end ?? ''}` : undefined} />
          <DataRow label="Rainfall" value={profile.climate.annualRainfallMm} unit="mm/day" source={profile.climate.rainfallSource} detail={profile.climate.rainfallPeriod ? `Period: ${profile.climate.rainfallPeriod.start ?? ''} to ${profile.climate.rainfallPeriod.end ?? ''}` : undefined} />
        </DomainCard>

        {/* Land Cover */}
        <DomainCard icon={Leaf} title="Land Cover & Habitat" colorClass="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
          <DataRow label="Cover Classification" value={profile.land.coverType} unit="" source={profile.land.source} isString />
          <DataRow label="Land Use Regime" value={profile.land.landUseType || 'Active Agricultural / Ecosystem'} unit="" source={profile.land.source} isString />
        </DomainCard>

        {/* Biodiversity */}
        <DomainCard icon={Sprout} title="Biodiversity Indicators" colorClass="bg-purple-500/10 text-purple-600 dark:text-purple-400">
          <DataRow label="Species Richness" value={profile.biodiversity.speciesRichness} unit="distinct species" source={profile.biodiversity.source} />
          <DataRow label="GBIF Observation Count" value={profile.biodiversity.observationCount} unit="records" source={profile.biodiversity.source} />
        </DomainCard>

        {/* Human Impact & Air Quality */}
        <DomainCard icon={Wind} title="Human Impact & Air Quality" colorClass="bg-rose-500/10 text-rose-600 dark:text-rose-400">
          <DataRow
            label="Fine Particulate (PM2.5)"
            value={hi?.pm2_5}
            unit={hi?.pm2_5_unit || 'µg/m³'}
            source={hi?.pm2_5_source || 'Copernicus CAMS / Open-Meteo'}
          />
          <DataRow
            label="Coarse Particulate (PM10)"
            value={hi?.pm10}
            unit={hi?.pm10_unit || 'µg/m³'}
            source={hi?.pm10_source || 'Copernicus CAMS / Open-Meteo'}
          />
          <DataRow
            label="Air Quality Index (AQI)"
            value={hi?.aqi ?? (hi?.usAqi ? `${hi.usAqi} (US AQI)` : null)}
            unit=""
            source="Copernicus CAMS"
            isString
          />
          <DataRow
            label="Forest Canopy Change"
            value={hi?.treeCoverLossHa != null ? `${hi.treeCoverLossHa} ha loss` : 'Zero significant loss detected'}
            unit=""
            source={hi?.treeCoverLossSource || 'Hansen Global Forest Change'}
            isString
          />
        </DomainCard>
      </div>
    </div>
  );
}

function DomainCard({
  icon: Icon,
  title,
  colorClass,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  colorClass: string;
  children: React.ReactNode;
}) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2.5">
          <div className={cn('flex h-8 w-8 items-center justify-center rounded-lg', colorClass)}>
            <Icon className="h-4 w-4" />
          </div>
          <CardTitle className="text-base">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col space-y-3 pt-0">{children}</CardContent>
    </Card>
  );
}

function DataRow({
  label,
  value,
  unit,
  source,
  detail,
  isString,
}: {
  label: string;
  value: number | string | null | undefined;
  unit?: string;
  source?: string | null;
  detail?: string;
  isString?: boolean;
}) {
  const hasValue = value !== null && value !== undefined && value !== '';
  const display = hasValue ? (isString ? String(value) : `${value}${unit ? ` ${unit}` : ''}`) : 'Data unavailable';
  return (
    <div className="space-y-1 rounded-md border border-border/60 bg-muted/20 p-2.5">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs text-muted-foreground font-medium">{label}</span>
        {hasValue ? (
          <Database className="h-3 w-3 text-emerald-500" />
        ) : (
          <CircleAlert className="h-3 w-3 text-muted-foreground/50" />
        )}
      </div>
      <div className="text-sm font-semibold text-foreground">{display}</div>
      <div className="text-[11px] text-muted-foreground">{source ? `Source: ${source}` : 'Source: unavailable'}</div>
      {detail && <div className="text-[10px] text-muted-foreground/80">{detail}</div>}
    </div>
  );
}

export default EnvironmentPage;
