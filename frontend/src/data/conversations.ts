import type { Conversation } from '@/models';

export const mockConversations: Conversation[] = [
  {
    id: 'conv-001',
    title: 'Willow Creek watershed assessment',
    messageCount: 6,
    createdAt: '2026-09-15T14:00:00Z',
    updatedAt: '2026-09-15T15:30:00Z',
    environmentalContext: {
      known: [
        { category: 'Soil', field: 'pH', value: '6.2' },
        { category: 'Soil', field: 'Organic Carbon', value: '2.8%' },
        { category: 'Climate', field: 'Annual Rainfall', value: '820 mm' },
        { category: 'Climate', field: 'Avg Temperature', value: '16.5°C' },
        { category: 'Land', field: 'Land Use', value: 'Mixed agriculture' },
        { category: 'Biodiversity', field: 'Species Richness', value: '72 species' },
      ],
      missing: [
        { category: 'Soil', field: 'Microbial Biomass', question: 'What is the soil microbial biomass carbon level?' },
        { category: 'Climate', field: 'Groundwater Depth', question: 'What is the current groundwater table depth?' },
        { category: 'Land', field: 'Historical Land Use', question: 'What was the land use pattern over the past decade?' },
      ],
    },
    messages: [
      {
        id: 'msg-001',
        role: 'user',
        content: 'Can you assess the overall environmental health of the Willow Creek Watershed?',
        timestamp: '2026-09-15T14:00:00Z',
      },
      {
        id: 'msg-002',
        role: 'assistant',
        content:
          'Based on the available environmental data, the Willow Creek Watershed shows a moderate environmental health score of 67/100. The area has adequate soil pH (6.2) and moderate organic carbon (2.8%), but faces challenges with soil moisture (34%, below optimal), moderate erosion risk, and a critical deforestation rate of 1.2%/yr. Habitat diversity (0.54) is below the regional benchmark of 0.65. I can provide detailed recommendations if you would like.',
        timestamp: '2026-09-15T14:01:00Z',
        evidenceRefs: ['ev-001', 'ev-004'],
      },
      {
        id: 'msg-003',
        role: 'user',
        content: 'Yes, what are the most urgent actions I should take?',
        timestamp: '2026-09-15T14:05:00Z',
      },
      {
        id: 'msg-004',
        role: 'assistant',
        content:
          'The four highest-priority actions are:\n\n1. Implement cover cropping across 60% of cropland (high priority, short-term) — increases soil carbon and moisture retention.\n\n2. Establish 20m riparian buffer zones along all waterways (high priority, medium-term) — reduces pollution runoff by 60–90% and creates habitat corridors.\n\n3. Adopt precision nutrient management (medium priority, short-term) — reduces nitrogen runoff by 30–50%.\n\n4. Transition 15% of land to agroforestry (medium priority, long-term) — supports 40–60% higher species richness.\n\nWould you like me to elaborate on any of these?',
        timestamp: '2026-09-15T14:06:00Z',
        evidenceRefs: ['ev-001', 'ev-002', 'ev-005', 'ev-006'],
      },
      {
        id: 'msg-005',
        role: 'user',
        content: 'Tell me more about the riparian buffer zones. How long until I see results?',
        timestamp: '2026-09-15T15:25:00Z',
      },
      {
        id: 'msg-006',
        role: 'assistant',
        content:
          'Riparian buffer zones of 20m width provide measurable water quality improvements within 1–2 years as vegetation establishes. Significant pollution reduction (60–90%) is typically observed within 3–5 years as the buffer matures. Biodiversity gains, including increased species richness and habitat connectivity, become more pronounced after 5–7 years. The meta-analysis from the Journal of Environmental Quality confirms these timelines across 60+ agricultural watersheds studied.',
        timestamp: '2026-09-15T15:30:00Z',
        evidenceRefs: ['ev-006'],
      },
    ],
  },
  {
    id: 'conv-002',
    title: 'Agroforestry transition planning',
    messageCount: 4,
    createdAt: '2026-09-12T09:00:00Z',
    updatedAt: '2026-09-12T10:00:00Z',
    environmentalContext: {
      known: [
        { category: 'Land', field: 'Area', value: '145 hectares' },
        { category: 'Land', field: 'Current Use', value: 'Mixed agriculture' },
        { category: 'Biodiversity', field: 'Species Richness', value: '72 species' },
      ],
      missing: [
        { category: 'Soil', field: 'Microbial Biomass', question: 'What is the soil microbial biomass carbon level?' },
        { category: 'Land', field: 'Tree Species Present', question: 'What native tree species are currently present?' },
      ],
    },
    messages: [
      {
        id: 'msg-007',
        role: 'user',
        content: 'I am considering converting 20% of my cropland to agroforestry. What impact would this have?',
        timestamp: '2026-09-12T09:00:00Z',
      },
      {
        id: 'msg-008',
        role: 'assistant',
        content:
          'Converting 20% of your 145 hectares (approximately 29 hectares) to agroforestry would have significant positive impacts. Based on FAO systematic review data, agroforestry systems in temperate climates support 40–60% higher species richness compared to monoculture croplands. For your watershed, this projects an increase from 72 to approximately 95 species. Soil organic carbon would also improve by an estimated 0.6 percentage points over 10 years.',
        timestamp: '2026-09-12T09:02:00Z',
        evidenceRefs: ['ev-002'],
      },
      {
        id: 'msg-009',
        role: 'user',
        content: 'Which tree species would you recommend for this region?',
        timestamp: '2026-09-12T09:45:00Z',
      },
      {
        id: 'msg-010',
        role: 'assistant',
        content:
          'For the Willow Creek Watershed in Oregon, I would recommend native species suited to the climate and soil conditions: Douglas fir and Oregon white oak for timber and biodiversity, red alder for nitrogen fixation, and walnut or chestnut for nut production. A mixed-species approach maximizes biodiversity benefits and spreads risk. I would need information about your specific soil microbial biomass and existing tree species to refine these recommendations.',
        timestamp: '2026-09-12T10:00:00Z',
      },
    ],
  },
  {
    id: 'conv-003',
    title: 'Drought resilience analysis',
    messageCount: 3,
    createdAt: '2026-09-05T08:00:00Z',
    updatedAt: '2026-09-05T08:30:00Z',
    environmentalContext: {
      known: [
        { category: 'Climate', field: 'Annual Rainfall', value: '820 mm' },
        { category: 'Climate', field: 'Temperature', value: '16.5°C' },
        { category: 'Soil', field: 'Moisture', value: '34%' },
      ],
      missing: [
        { category: 'Climate', field: 'Rainfall Variability', question: 'What is the inter-annual rainfall variability?' },
        { category: 'Climate', field: 'Groundwater Depth', question: 'What is the current groundwater table depth?' },
      ],
    },
    messages: [
      {
        id: 'msg-011',
        role: 'user',
        content: 'How would a 20% reduction in annual rainfall affect my soil and crops?',
        timestamp: '2026-09-05T08:00:00Z',
      },
      {
        id: 'msg-012',
        role: 'assistant',
        content:
          'A 20% reduction in annual rainfall (from 820mm to 656mm) would have significant impacts. Soil moisture, currently at 34%, would likely decrease to approximately 24% within 3 years, approaching critical levels for most crops. Crop yields in rain-fed systems would decline by an estimated 25–35% based on World Bank correlation data. I recommend installing drip irrigation and implementing water conservation practices to mitigate these effects.',
        timestamp: '2026-09-05T08:05:00Z',
        evidenceRefs: ['ev-003', 'ev-011'],
      },
      {
        id: 'msg-013',
        role: 'user',
        content: 'What water conservation practices would be most effective?',
        timestamp: '2026-09-05T08:25:00Z',
      },
    ],
  },
];
