from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.scenario_manager import ScenarioManager
from app.schemas import ScenarioResponse, ScenarioCreate, ScenarioUpdate


router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.get("/", response_model=List[ScenarioResponse])
def list_scenarios(db: Session = Depends(get_db)):
    """Get list of all active scenarios."""
    manager = ScenarioManager(db)
    scenarios = manager.get_all_active()
    return scenarios


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get scenario by ID."""
    manager = ScenarioManager(db)
    scenario = manager.get_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.post("/", response_model=ScenarioResponse, status_code=201)
def create_scenario(
    scenario_data: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create new scenario."""
    manager = ScenarioManager(db)
    scenario = manager.create(scenario_data)
    return scenario


@router.put("/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(
    scenario_id: int,
    scenario_data: ScenarioUpdate,
    db: Session = Depends(get_db)
):
    """Update existing scenario."""
    manager = ScenarioManager(db)
    try:
        scenario = manager.update(scenario_id, scenario_data)
        return scenario
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Deactivate scenario (soft delete)."""
    manager = ScenarioManager(db)
    scenario = manager.get_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    manager.delete(scenario_id)
    return None
