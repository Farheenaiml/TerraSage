from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDefinition:
    title: str
    organization: str
    year: int | None
    source_type: str
    source_url: str
    topic: str
    environmental_metrics: tuple[str, ...]


CURATED_SOURCES = (
    SourceDefinition(
        title="Recarbonizing Global Soils: A Technical Manual of Recommended Sustainable Soil Management",
        organization="Food and Agriculture Organization of the United Nations",
        year=2021,
        source_type="technical-manual",
        source_url="https://openknowledge.fao.org/3/cb6385en/cb6385en.pdf",
        topic="soil organic carbon and sustainable soil management",
        environmental_metrics=("soil_ph", "soil_organic_carbon", "soil_moisture", "agriculture", "land_degradation"),
    ),
    SourceDefinition(
        title="The State of the World's Biodiversity for Food and Agriculture",
        organization="Food and Agriculture Organization of the United Nations",
        year=2019,
        source_type="assessment-report",
        source_url="https://openknowledge.fao.org/3/ca3129en/ca3129en.pdf",
        topic="biodiversity for food and agriculture",
        environmental_metrics=("species_richness", "habitat_diversity", "soil_biodiversity", "agriculture"),
    ),
    SourceDefinition(
        title="State of Knowledge of Soil Biodiversity",
        organization="Food and Agriculture Organization of the United Nations",
        year=2020,
        source_type="technical-report",
        source_url="https://openknowledge.fao.org/3/cb1928en/cb1928en.pdf",
        topic="soil biodiversity, carbon, nutrient cycling and land degradation",
        environmental_metrics=("soil_biodiversity", "soil_organic_carbon", "pollution", "land_degradation"),
    ),
    SourceDefinition(
        title="Climate Change and Land",
        organization="Intergovernmental Panel on Climate Change",
        year=2019,
        source_type="government-report",
        source_url="https://www.ipcc.ch/srccl/",
        topic="climate, land use, land degradation, biodiversity, water",
        environmental_metrics=("temperature", "rainfall", "land_use", "land_degradation", "biodiversity", "water_availability"),
    ),
    SourceDefinition(
        title="Conservation Agriculture",
        organization="Food and Agriculture Organization of the United Nations",
        year=None,
        source_type="guideline",
        source_url="https://www.fao.org/conservation-agriculture/en/",
        topic="soil cover, crop diversification, soil moisture, biodiversity",
        environmental_metrics=("soil_moisture", "soil_biodiversity", "vegetation", "agriculture", "cover_crops"),
    ),
)
