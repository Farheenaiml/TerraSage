from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def new_id() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    profiles: Mapped[list["EnvironmentalProfile"]] = relationship(back_populates="user")


class EnvironmentalProfile(Base):
    __tablename__ = "environmental_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[str | None] = mapped_column(String(200), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="profiles")
    soil: Mapped["SoilMetric | None"] = relationship(back_populates="profile", cascade="all, delete-orphan", uselist=False)
    climate: Mapped["ClimateMetric | None"] = relationship(back_populates="profile", cascade="all, delete-orphan", uselist=False)
    land: Mapped["LandMetric | None"] = relationship(back_populates="profile", cascade="all, delete-orphan", uselist=False)
    biodiversity: Mapped["BiodiversityMetric | None"] = relationship(back_populates="profile", cascade="all, delete-orphan", uselist=False)
    human_impact: Mapped["HumanImpactMetric | None"] = relationship(back_populates="profile", cascade="all, delete-orphan", uselist=False)


class MetricBase:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    profile_id: Mapped[str] = mapped_column(ForeignKey("environmental_profiles.id", ondelete="CASCADE"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SoilMetric(MetricBase, Base):
    __tablename__ = "soil_metrics"
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    organic_carbon: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    profile: Mapped[EnvironmentalProfile] = relationship(back_populates="soil")


class ClimateMetric(MetricBase, Base):
    __tablename__ = "climate_metrics"
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall: Mapped[float | None] = mapped_column(Float, nullable=True)
    profile: Mapped[EnvironmentalProfile] = relationship(back_populates="climate")


class LandMetric(MetricBase, Base):
    __tablename__ = "land_metrics"
    land_use: Mapped[str | None] = mapped_column(String(200), nullable=True)
    land_cover: Mapped[str | None] = mapped_column(String(200), nullable=True)
    profile: Mapped[EnvironmentalProfile] = relationship(back_populates="land")


class BiodiversityMetric(MetricBase, Base):
    __tablename__ = "biodiversity_metrics"
    species_richness: Mapped[float | None] = mapped_column(Float, nullable=True)
    habitat_diversity: Mapped[float | None] = mapped_column(Float, nullable=True)
    profile: Mapped[EnvironmentalProfile] = relationship(back_populates="biodiversity")


class HumanImpactMetric(MetricBase, Base):
    __tablename__ = "human_impact_metrics"
    pollution: Mapped[float | None] = mapped_column(Float, nullable=True)
    deforestation: Mapped[float | None] = mapped_column(Float, nullable=True)
    profile: Mapped[EnvironmentalProfile] = relationship(back_populates="human_impact")


class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    location_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    source: Mapped[str] = mapped_column(String(200), index=True)
    metric: Mapped[str] = mapped_column(String(200), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    depth_or_layer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    observation_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    period_start: Mapped[str | None] = mapped_column(String(50), nullable=True)
    period_end: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    raw_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProviderCache(Base):
    __tablename__ = "provider_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    cache_key: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(200), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    parameters: Mapped[str | None] = mapped_column(String(500), nullable=True)
    time_period: Mapped[str | None] = mapped_column(String(200), nullable=True)
    dataset_version: Mapped[str | None] = mapped_column(String(200), nullable=True)
    response_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
