from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .. import crud, models
from ..database import get_db
from ..schemas import trade_schemas as schemas

router = APIRouter(prefix="/positions", tags=["positions"])

@router.post("/", response_model=schemas.Position)
def create_position(position: schemas.PositionCreate, db: Session = Depends(get_db)):
    return crud.create_position(db=db, position=position)

@router.get("/", response_model=List[schemas.Position])
def read_positions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    positions = crud.get_positions(db, skip=skip, limit=limit)
    return positions

@router.get("/{position_id}", response_model=schemas.Position)
def read_position(position_id: int, db: Session = Depends(get_db)):
    position = crud.get_position_by_id(db, position_id=position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.put("/{position_id}", response_model=schemas.Position)
def update_position(position_id: int, position: schemas.PositionUpdate, db: Session = Depends(get_db)):
    db_position = crud.update_position(db, position_id=position_id, position=position)
    if db_position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return db_position

@router.delete("/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    success = crud.delete_position(db, position_id=position_id)
    if not success:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"message": "Position deleted successfully"}