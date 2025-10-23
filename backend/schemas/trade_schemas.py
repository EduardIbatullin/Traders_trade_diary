from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NoteBase(BaseModel):
    text: Optional[str] = None
    category: Optional[str] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    
    class Config:
        from_attributes = True


class TradeBase(BaseModel):
    instrument: str
    trade_date: datetime
    operation: str
    quantity: float
    price: float
    commission: Optional[float] = 0.0


class TradeCreate(TradeBase):
    note_id: Optional[int] = None


class TradeUpdate(BaseModel):
    instrument: Optional[str] = None
    trade_date: Optional[datetime] = None
    operation: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    commission: Optional[float] = None
    note_id: Optional[int] = None


class Trade(TradeBase):
    id: int
    note_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    instrument: str


class PositionCreate(PositionBase):
    avg_price: Optional[float] = None
    quantity_total: Optional[float] = None
    total_commission: Optional[float] = None


class PositionUpdate(BaseModel):
    avg_price: Optional[float] = None
    quantity_total: Optional[float] = None
    total_commission: Optional[float] = None
    total_profit_loss_value: Optional[float] = None
    total_profit_loss_percent: Optional[float] = None
    note_id: Optional[int] = None


class Position(PositionBase):
    id: int
    avg_price: Optional[float] = None
    quantity_total: Optional[float] = None
    total_commission: Optional[float] = None
    total_profit_loss_value: Optional[float] = None
    total_profit_loss_percent: Optional[float] = None
    note_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True