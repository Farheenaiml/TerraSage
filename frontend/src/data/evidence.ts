import type {
  EvidenceReference,
  EvidenceType,
} from '@/models';

export const mockEvidence: EvidenceReference[] = [
  {
    id: 'ev-001',
    title: 'Soil Organic Carbon Sequestration in Agricultural Lands',
    source: 'Nature Climate Change',
    organization: 'IPCC',
    year: 2023,
    type: 'peer-reviewed',
    metrics: ['soil-organic-carbon', 'carbon-sequestration', 'climate-mitigation'],
    url: 'https://example.org/evidence/soil-carbon-sequestration',
    summary:
      'Meta-analysis of 142 studies showing that cover cropping and reduced tillage increase soil organic carbon by 0.4–1.2 t C/ha/yr over 10–20 year periods.',
    relevanceScore: 0.94,
  },
  {
    id: 'ev-002',
    title: 'Impact of Agroforestry on Biodiversity in Temperate Regions',
    source: 'Agriculture, Ecosystems & Environment',
    organization: 'FAO',
    year: 2022,
    type: 'peer-reviewed',
    metrics: ['biodiversity', 'species-richness', 'habitat-diversity', 'agroforestry'],
    url: 'https://example.org/evidence/agroforestry-biodiversity',
    summary:
      'Systematic review demonstrating agroforestry systems support 40–60% higher species richness compared to monoculture croplands in temperate climates.',
    relevanceScore: 0.88,
  },
  {
    id: 'ev-003',
    title: 'Rainfall Variability and Crop Yield Correlation in Sub-Saharan Africa',
    source: 'Global Environmental Change',
    organization: 'World Bank',
    year: 2024,
    type: 'peer-reviewed',
    metrics: ['rainfall', 'crop-yield', 'climate-variability'],
    url: 'https://example.org/evidence/rainfall-crop-yield',
    summary:
      'Analysis of 30 years of rainfall data showing strong correlation between growing-season rainfall variability and crop yield decline in rain-fed agricultural systems.',
    relevanceScore: 0.91,
  },
  {
    id: 'ev-004',
    title: 'Global Assessment of Land Degradation and Restoration',
    source: 'IPBES Assessment Report',
    organization: 'IPBES',
    year: 2022,
    type: 'government-report',
    metrics: ['land-degradation', 'restoration', 'deforestation', 'biodiversity'],
    url: 'https://example.org/evidence/land-degradation-assessment',
    summary:
      'Comprehensive assessment finding 75% of terrestrial ecosystems are significantly altered by human activity, with restoration potential identified in 2 billion hectares.',
    relevanceScore: 0.86,
  },
  {
    id: 'ev-005',
    title: 'Nitrogen Use Efficiency in Sustainable Agriculture',
    source: 'Environmental Research Letters',
    organization: 'FAO',
    year: 2023,
    type: 'peer-reviewed',
    metrics: ['soil-nutrients', 'nitrogen', 'pollution', 'agriculture'],
    url: 'https://example.org/evidence/nitrogen-efficiency',
    summary:
      'Study showing precision nutrient management reduces nitrogen runoff by 30–50% while maintaining or improving crop yields.',
    relevanceScore: 0.82,
  },
  {
    id: 'ev-006',
    title: 'Riparian Buffer Zones for Water Quality Protection',
    source: 'Journal of Environmental Quality',
    organization: 'EPA',
    year: 2021,
    type: 'peer-reviewed',
    metrics: ['water-quality', 'pollution', 'riparian-buffer', 'biodiversity'],
    url: 'https://example.org/evidence/riparian-buffers',
    summary:
      'Meta-analysis confirming riparian buffer zones of 10–30m reduce nutrient and sediment runoff by 60–90% in agricultural watersheds.',
    relevanceScore: 0.90,
  },
  {
    id: 'ev-007',
    title: 'Habitat Fragmentation and Species Extinction Risk',
    source: 'Conservation Biology',
    organization: 'IUCN',
    year: 2023,
    type: 'peer-reviewed',
    metrics: ['habitat-diversity', 'species-richness', 'fragmentation', 'biodiversity'],
    url: 'https://example.org/evidence/habitat-fragmentation',
    summary:
      'Review of 89 studies showing habitat fragmentation increases local extinction risk by 20–40% for specialist species in fragmented landscapes.',
    relevanceScore: 0.85,
  },
  {
    id: 'ev-008',
    title: 'Regenerative Agriculture Practices and Soil Health Indicators',
    source: 'Soil Biology and Biochemistry',
    organization: 'Rodale Institute',
    year: 2024,
    type: 'meta-analysis',
    metrics: ['soil-health', 'organic-carbon', 'microbial-biomass', 'regenerative-agriculture'],
    url: 'https://example.org/evidence/regenerative-soil-health',
    summary:
      'Meta-analysis of 55 trials showing regenerative practices (cover crops, diversified rotations, organic amendments) increase soil microbial biomass by 30–70%.',
    relevanceScore: 0.93,
  },
  {
    id: 'ev-009',
    title: 'Urban Heat Island Effects on Microclimate and Biodiversity',
    source: 'Landscape and Urban Planning',
    organization: 'UN-Habitat',
    year: 2022,
    type: 'peer-reviewed',
    metrics: ['temperature', 'urban-heat-island', 'biodiversity', 'microclimate'],
    url: 'https://example.org/evidence/urban-heat-island',
    summary:
      'Study quantifying urban heat island effects, showing 2–5°C temperature increases in dense urban areas with corresponding biodiversity loss.',
    relevanceScore: 0.78,
  },
  {
    id: 'ev-010',
    title: 'Sustainable Land Management Guidelines for Smallholder Farmers',
    source: 'Technical Guidelines Series',
    organization: 'FAO',
    year: 2023,
    type: 'guideline',
    metrics: ['land-management', 'soil-conservation', 'sustainable-agriculture'],
    url: 'https://example.org/evidence/slm-guidelines',
    summary:
      'Practical guidelines for implementing sustainable land management practices including contour farming, terracing, and agroforestry integration.',
    relevanceScore: 0.80,
  },
  {
    id: 'ev-011',
    title: 'Deforestation Trends and Carbon Emissions in Tropical Forests',
    source: 'Global Forest Resources Assessment',
    organization: 'FAO',
    year: 2023,
    type: 'dataset',
    metrics: ['deforestation', 'carbon-emissions', 'tropical-forests', 'land-use-change'],
    url: 'https://example.org/evidence/deforestation-trends',
    summary:
      'Remote sensing analysis of tropical forest loss from 2000–2023, showing 10 million hectares lost annually with associated 4.8 Gt CO2 emissions.',
    relevanceScore: 0.87,
  },
  {
    id: 'ev-012',
    title: 'Water Stress Indicators and Agricultural Water Use Efficiency',
    source: 'Water Resources Research',
    organization: 'World Resources Institute',
    year: 2024,
    type: 'peer-reviewed',
    metrics: ['water-stress', 'irrigation-efficiency', 'water-management', 'agriculture'],
    url: 'https://example.org/evidence/water-stress',
    summary:
      'Analysis of global water stress indicators showing 40% of agricultural land faces high water stress, with drip irrigation reducing water use by 40–60%.',
    relevanceScore: 0.84,
  },
];

export const evidenceTypeLabels: Record<EvidenceType, string> = {
  'peer-reviewed': 'Peer-Reviewed Study',
  'government-report': 'Government Report',
  'ngo-report': 'NGO Report',
  dataset: 'Dataset',
  guideline: 'Guideline',
  'meta-analysis': 'Meta-Analysis',
};

export function getEvidenceByIds(ids: string[]): EvidenceReference[] {
  return mockEvidence.filter((e) => ids.includes(e.id));
}
