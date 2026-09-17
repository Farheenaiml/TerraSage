import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.environment import EnvironmentalObservation, ProviderCache
from app.environmental_data.service import build_environmental_profile, collect_environmental_data, validate_coordinates
from app.environmental_data.cache import CacheRepository
from app.environmental_data.providers.nasa_power import parse_nasa_power_response
from app.environmental_data.providers.soilgrids import parse_soilgrids_response, SoilGridsProvider
from app.environmental_data.providers.worldcover import classify_worldcover_response, get_worldcover_tile_id
from app.environmental_data.providers.gbif import parse_gbif_response


@pytest.mark.parametrize(
    "latitude,longitude",
    [(91, 72.8777), (-91.01, 72.8777), (19.076, 181), (19.076, -181.1)],
)
def test_coordinate_validation_rejects_out_of_range(latitude, longitude):
    with pytest.raises(ValueError):
        validate_coordinates(latitude, longitude)


def test_nasa_power_response_parsing_and_units():
    payload = {
        "properties": {
            "parameter": {
                "T2M": {"202301": 22.2, "202313": 27.0},
                "PRECTOTCORR": {"202301": 0.01, "202313": 7.29},
            }
        },
        "geometry": {"coordinates": [72.8777, 19.076]},
    }
    observations = parse_nasa_power_response(payload, latitude=19.076, longitude=72.8777)
    
    # Check metric and units
    temps = [o for o in observations if o["metric"] == "temperature"]
    rains = [o for o in observations if o["metric"] == "rainfall"]
    assert len(temps) == 2
    assert len(rains) == 2
    assert all(o["unit"] == "C" for o in temps)
    assert all(o["unit"] == "mm/day" for o in rains)
    
    # Check annual average metadata
    annual_temp = next(o for o in temps if o["metadata"]["is_annual_average"])
    assert annual_temp["value"] == 27.0
    assert annual_temp["metadata"]["original_parameter"] == "T2M"

    annual_rain = next(o for o in rains if o["metadata"]["is_annual_average"])
    assert annual_rain["value"] == 7.29
    assert annual_rain["metadata"]["rainfall_representation"] == "mean_daily_precipitation"
    assert annual_rain["metadata"]["accumulated_precipitation_mm"] > 0


def test_soilgrids_unit_conversion_and_metadata():
    payload = {
        "properties": {
            "layers": [
                {
                    "name": "phhox",
                    "depths": [{"name": "0-5cm", "values": {"mean": 65, "uncertainty": 5}}],
                },
                {
                    "name": "soc",
                    "depths": [{"name": "0-5cm", "values": {"mean": 180, "uncertainty": 12}}],
                },
            ]
        },
        "lat": 19.076,
        "lon": 72.8777,
    }
    observations = parse_soilgrids_response(payload, latitude=19.076, longitude=72.8777)
    
    ph_obs = next(o for o in observations if o["metric"] == "soil_pH")
    soc_obs = next(o for o in observations if o["metric"] == "soil_organic_carbon")
    
    # 65 with conversion_factor 0.1 -> 6.5 pH
    assert ph_obs["value"] == 6.5
    assert ph_obs["unit"] == "pH"
    assert ph_obs["metadata"]["original_value"] == 65
    assert ph_obs["metadata"]["conversion_factor"] == 0.1
    
    # 180 with conversion_factor 0.1 -> 18.0 g/kg
    assert soc_obs["value"] == 18.0
    assert soc_obs["unit"] == "g/kg"
    assert soc_obs["metadata"]["original_value"] == 180
    assert soc_obs["metadata"]["conversion_factor"] == 0.1


def test_soilgrids_unavailable_state(monkeypatch):
    provider = SoilGridsProvider()
    # When upstream fails or is paused
    monkeypatch.setattr("httpx.get", lambda *a, **k: (_ for _ in ()).throw(Exception("Connection refused")))
    res = provider.get_data(19.076, 72.8777)
    assert res["status"] == "UNAVAILABLE"
    assert res["observations"] == []
    assert "unavailable upstream" in res["message"]


def test_worldcover_raster_class_parsing():
    # Tile computation
    tile_id = get_worldcover_tile_id(19.076, 72.8777)
    assert tile_id == "ESA_WorldCover_10m_2021_v200_N18E072"

    payload = {"values": [50.0], "coordinates": [72.8777, 19.076]}
    record = classify_worldcover_response(payload, latitude=19.076, longitude=72.8777, tile_id=tile_id)
    assert record["class_name"] == "Built-up"
    assert record["class_code"] == 50
    assert record["metadata"]["tile_id"] == "ESA_WorldCover_10m_2021_v200_N18E072"
    assert record["metadata"]["dataset"] == "ESA WorldCover"


def test_gbif_occurrence_parsing_and_distinct_species():
    # Test with complete native Solr facet aggregation
    payload_facet = {
        "count": 338380,
        "facets": [
            {
                "field": "SPECIES_KEY",
                "counts": [
                    {"name": "101", "count": 18000},
                    {"name": "102", "count": 14000},
                    {"name": "103", "count": 9000},
                ],
            }
        ],
    }
    obs_facet = parse_gbif_response(payload_facet, latitude=19.076, longitude=72.8777, radius_km=10)
    assert obs_facet[0]["value"] == 338380
    assert obs_facet[1]["value"] == 3
    assert obs_facet[1]["metadata"]["aggregation_method"] == "full_dataset_speciesKey_facet"
    assert "Observed species richness from GBIF occurrence records" in obs_facet[1]["metadata"]["indicator_name"]

    # Test with results list fallback
    payload_results = {
        "count": 1250,
        "results": [
            {"speciesKey": 101, "species": "Ficus benghalensis"},
            {"speciesKey": 102, "species": "Azadirachta indica"},
            {"speciesKey": 101, "species": "Ficus benghalensis"}, # duplicate
            {"speciesKey": None, "scientificName": "Unknown Plantae"}, # no reliable taxonomic key
        ],
    }
    obs = parse_gbif_response(payload_results, latitude=19.076, longitude=72.8777, radius_km=10)
    
    count_obs = next(o for o in observations if o["metric"] == "observation_count") if False else obs[0]
    species_obs = next(o for o in observations if o["metric"] == "distinct_species_count") if False else obs[1]
    
    assert count_obs["value"] == 1250
    assert species_obs["value"] == 2 # Only 101 and 102


def test_cache_behavior():
    if SessionLocal is None:
        pytest.skip("Database not configured")
    db = SessionLocal()
    cache = CacheRepository(db)
    
    # Store a successful result
    cache.set(
        provider="test_prov",
        latitude=19.076,
        longitude=72.8777,
        params="k=v",
        period="default",
        dataset_version="default",
        response={"status": "AVAILABLE", "val": 42},
    )
    
    cached = cache.get(
        provider="test_prov",
        latitude=19.076,
        longitude=72.8777,
        params="k=v",
        period="default",
        dataset_version="default",
    )
    assert cached is not None
    assert cached["val"] == 42
    
    # Clean up test cache entry
    db.query(ProviderCache).filter(ProviderCache.provider == "test_prov").delete()
    db.commit()
    db.close()


def test_database_persistence():
    if SessionLocal is None:
        pytest.skip("Database not configured")
    db = SessionLocal()
    from app.api.routes.environment import persist_observations
    
    test_lat, test_lon = 88.1234, 123.4567
    loc_id = f"coord:{test_lat:.6f}:{test_lon:.6f}"
    
    test_obs = [
        {
            "metric": "temperature",
            "value": 26.5,
            "unit": "C",
            "source": "NASA POWER",
            "period_start": "2023-01-01",
            "period_end": "2023-12-31",
            "metadata": {"test": True},
        }
    ]
    try:
        persist_observations(db, test_lat, test_lon, test_obs)
        
        record = (
            db.query(EnvironmentalObservation)
            .filter(EnvironmentalObservation.location_id == loc_id)
            .filter(EnvironmentalObservation.metric == "temperature")
            .first()
        )
        assert record is not None
        assert record.value == 26.5
        assert record.source == "NASA POWER"
    finally:
        db.query(EnvironmentalObservation).filter(EnvironmentalObservation.location_id == loc_id).delete()
        db.commit()
        db.close()


def test_build_environmental_profile_aggregates_real_measures():
    profile = build_environmental_profile(
        latitude=19.076,
        longitude=72.8777,
        observations=[
            {"metric": "soil_pH", "value": 6.4, "unit": "pH", "depth_or_layer": "0-5cm", "source": "SoilGrids"},
            {"metric": "soil_organic_carbon", "value": 1.7, "unit": "g/kg", "depth_or_layer": "0-5cm", "source": "SoilGrids"},
            {"metric": "temperature", "value": 27.0, "unit": "C", "source": "NASA POWER", "period_start": "2023-01-01", "period_end": "2023-12-31", "metadata": {"is_annual_average": True}},
            {"metric": "rainfall", "value": 7.29, "unit": "mm/day", "source": "NASA POWER", "period_start": "2023-01-01", "period_end": "2023-12-31", "metadata": {"is_annual_average": True, "accumulated_precipitation_mm": 2660.85}},
            {"metric": "land_cover_class", "value": "Built-up", "source": "ESA WorldCover 2021", "metadata": {"land_cover_class_code": 50}},
            {"metric": "distinct_species_count", "value": 35, "unit": "species", "source": "GBIF"},
        ],
    )
    assert profile["soil"]["ph"] == 6.4
    assert profile["climate"]["temperature"] == 27.0
    assert profile["climate"]["rainfall"] == 7.29
    assert profile["climate"]["accumulated_rainfall_mm"] == 2660.85
    assert profile["land"]["land_cover"] == "Built-up"
    assert profile["biodiversity"]["observed_species_richness"] == 35


def test_environment_api_rejects_bad_coordinates():
    client = TestClient(app)
    response = client.post("/api/environment/data", json={"latitude": 999, "longitude": 72.8777})
    assert response.status_code == 422
