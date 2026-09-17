from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import EnvironmentalProfile, User


class EnvironmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: str) -> EnvironmentalProfile | None:
        statement = (
            select(EnvironmentalProfile)
            .options(
                joinedload(EnvironmentalProfile.soil),
                joinedload(EnvironmentalProfile.climate),
                joinedload(EnvironmentalProfile.land),
                joinedload(EnvironmentalProfile.biodiversity),
                joinedload(EnvironmentalProfile.human_impact),
            )
            .where(EnvironmentalProfile.user_id == user_id)
            .order_by(EnvironmentalProfile.updated_at.desc())
        )
        return self.db.scalars(statement).first()

    def ensure_user(self, user_id: str) -> None:
        if self.db.get(User, user_id) is None:
            self.db.add(User(id=user_id, email=f"{user_id}@local.terrasage"))
            self.db.flush()

    def save_profile(self, profile: EnvironmentalProfile) -> EnvironmentalProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
