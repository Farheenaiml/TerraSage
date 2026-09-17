import type { EnvironmentalProfile } from '@/models';
import { request } from './http';

function normalizeProfile(profile: any): EnvironmentalProfile | null {
  if (!profile) return null;
  const soil = profile.soil ?? {};
  const climate = profile.climate ?? {};
  const land = profile.land ?? {};
  const biodiversity = profile.biodiversity ?? {};
  const hi = profile.human_impact ?? profile.humanImpact ?? {};

  return {
    id: profile.id ?? 'real-data-profile',
    userId: profile.userId ?? 'real-data',
    latitude: profile.location?.latitude ?? profile.latitude ?? null,
    longitude: profile.location?.longitude ?? profile.longitude ?? null,
    locationName: profile.locationName ?? profile.region ?? 'Environmental site',
    region: profile.region ?? null,
    updatedAt: profile.updatedAt ?? new Date().toISOString(),
    soil: {
      ph: soil.ph ?? null,
      organicCarbonPercent: soil.organic_carbon ?? soil.organicCarbon ?? null,
      moisturePercent: soil.moisture ?? null,
      source: soil.source ?? soil.organic_carbon_source ?? null,
      depth: soil.depth ?? soil.organic_carbon_depth ?? null,
    },
    climate: {
      annualRainfallMm: climate.rainfall ?? null,
      avgTemperatureC: climate.temperature ?? null,
      temperatureSource: climate.temperature_source ?? null,
      rainfallSource: climate.rainfall_source ?? null,
      temperaturePeriod: climate.temperature_period ?? null,
      rainfallPeriod: climate.rainfall_period ?? null,
    },
    land: {
      landUseType: land.land_use ?? null,
      coverType: land.land_cover ?? null,
      source: land.source ?? null,
    },
    biodiversity: {
      speciesRichness: biodiversity.observed_species_richness ?? biodiversity.species_richness ?? null,
      habitatDiversityIndex: biodiversity.habitat_diversity ?? null,
      source: biodiversity.observed_species_richness_source ?? biodiversity.source ?? null,
      observationCount: biodiversity.observation_count ?? null,
    },
    humanImpact: {
      pollutionIndex: hi.pm2_5 ?? hi.us_aqi ?? null,
      deforestationRatePercent: hi.deforestation_rate_percent ?? null,
      pm2_5: hi.pm2_5 ?? null,
      pm2_5_unit: hi.pm2_5_unit ?? 'µg/m³',
      pm2_5_source: hi.pm2_5_source ?? null,
      pm10: hi.pm10 ?? null,
      pm10_unit: hi.pm10_unit ?? 'µg/m³',
      pm10_source: hi.pm10_source ?? null,
      aqi: hi.aqi ?? hi.us_aqi ?? hi.european_aqi ?? null,
      europeanAqi: hi.european_aqi ?? null,
      usAqi: hi.us_aqi ?? null,
      treeCoverLossHa: hi.tree_cover_loss_total_ha ?? null,
      treeCoverLossSource: hi.tree_cover_loss_source ?? null,
      forestChangePeriod: hi.forest_change_period ?? null,
    },
    completenessPercent: 0,
  };
}

export const environmentService = {
  async getProfile(latitude?: number, longitude?: number): Promise<EnvironmentalProfile | null> {
    if (typeof latitude === 'number' && typeof longitude === 'number') {
      return request<any>(`/api/environment/profile?latitude=${latitude}&longitude=${longitude}`).then(normalizeProfile);
    }
    return request<any>('/api/environment/profile').then(normalizeProfile);
  },

  async getData(latitude: number, longitude: number, radiusKm = 10): Promise<any> {
    return request<any>(`/api/environment/data`, {
      method: 'POST',
      body: JSON.stringify({ latitude, longitude, radius_km: radiusKm }),
    });
  },

  async updateProfile(profile: Partial<EnvironmentalProfile>): Promise<EnvironmentalProfile> {
    return request<any>('/api/environment/profile', {
      method: 'PATCH',
      body: JSON.stringify(profile),
    }).then(normalizeProfile) as Promise<EnvironmentalProfile>;
  },
};

export { normalizeProfile };
