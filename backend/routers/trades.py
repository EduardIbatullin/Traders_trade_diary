from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .. import crud, models
from ..database import get_db
from ..schemas import trade_schemas as schemas

router = APIRouter(prefix="/trades", tags=["trades"])

@router.post("/", response_model=schemas.Trade)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    return crud.create_trade(db=db, trade=trade)

@router.get("/", response_model=List[schemas.Trade])
def read_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trades = crud.get_trades(db, skip=skip, limit=limit)
    return trades

@router.get("/{trade_id}", response_model=schemas.Trade)
def read_trade(trade_id: int, db: Session = Depends(get_db)):
    trade = crud.get_trade(db, trade_id=trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@router.put("/{trade_id}", response_model=schemas.Trade)
def update_trade(trade_id: int, trade: schemas.TradeUpdate, db: Session = Depends(get_db)):
    db_trade = crud.update_trade(db, trade_id=trade_id, trade=trade)
    if db_trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return db_trade

@router.delete("/{trade_id}")
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    success = crud.delete_trade(db, trade_id=trade_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trade not found")
    return {"message": "Trade deleted successfully"}