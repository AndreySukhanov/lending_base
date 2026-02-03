from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.scenario import Scenario
from app.schemas import ScenarioCreate, ScenarioUpdate


class ScenarioManager:
    """Service for managing scenarios."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_active(self) -> List[Scenario]:
        """Get all active scenarios ordered by order_index."""
        return (
            self.db.query(Scenario)
            .filter(Scenario.active == True)
            .order_by(Scenario.order_index)
            .all()
        )

    def get_by_id(self, scenario_id: int) -> Optional[Scenario]:
        """Get scenario by ID."""
        return self.db.query(Scenario).filter(Scenario.id == scenario_id).first()

    def create(self, scenario_data: ScenarioCreate) -> Scenario:
        """Create new scenario."""
        scenario = Scenario(**scenario_data.model_dump())
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def update(self, scenario_id: int, scenario_data: ScenarioUpdate) -> Scenario:
        """Update existing scenario."""
        scenario = self.get_by_id(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario with id {scenario_id} not found")

        # Update only provided fields
        for key, value in scenario_data.model_dump(exclude_unset=True).items():
            setattr(scenario, key, value)

        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def delete(self, scenario_id: int):
        """Deactivate scenario (soft delete)."""
        scenario = self.get_by_id(scenario_id)
        if scenario:
            scenario.active = False
            self.db.commit()
