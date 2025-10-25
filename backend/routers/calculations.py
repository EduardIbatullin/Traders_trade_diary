from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .. import crud, models, schemas
from ..database import get_db
from ..calculations import calculate_position_pnl
from ..schemas import trade_schemas as schemas

router = APIRouter(prefix="/calculations", tags=["calculations"])

@router.get("/position/{position_id}/pnl")
def get_position_pnl(position_id: int, current_price: float, db: Session = Depends(get_db)):
    """
    Получить расчеты P/L для позиции на основе текущей цены
    """
    position = crud.get_position_by_id(db, position_id=position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    trades = crud.get_trades_by_instrument(db, position.instrument)
    if not trades:
        return {
            "total_profit_loss_value": 0,
            "total_profit_loss_percent": 0,
            "quantity_held": 0,
            "avg_price": None
        }
    
    pnl_data = calculate_position_pnl(trades, current_price)
    return pnl_data

@router.get("/position/{instrument}/avg-price")
def get_position_avg_price(instrument: str, db: Session = Depends(get_db)):
    """
    Рассчитать среднюю цену позиции по инструменту
    """
    trades = crud.get_trades_by_instrument(db, instrument)
    if not trades:
        raise HTTPException(status_code=404, detail="No trades found for this instrument")
    
    from ..calculations import calculate_average_price
    avg_price = calculate_average_price(trades)
    
    if avg_price is None:
        return {"avg_price": None}
    
    return {"avg_price": float(avg_price)}