from sqlalchemy.orm import Session
from typing import List
from . import models, schemas

def get_trade(db: Session, trade_id: int):
    return db.query(models.Trade).filter(models.Trade.id == trade_id).first()

def get_trades(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Trade).offset(skip).limit(limit).all()

def create_trade(db: Session, trade: schemas.TradeCreate):
    db_trade = models.Trade(**trade.model_dump())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def update_trade(db: Session, trade_id: int, trade: schemas.TradeUpdate):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade:
        update_data = trade.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_trade, field, value)
        db.commit()
        db.refresh(db_trade)
    return db_trade

def delete_trade(db: Session, trade_id: int):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade:
        db.delete(db_trade)
        db.commit()
        return True
    return False

def get_position_by_instrument(db: Session, instrument: str):
    return db.query(models.Position).filter(models.Position.instrument == instrument).first()

def get_positions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Position).offset(skip).limit(limit).all()

def create_position(db: Session, position: schemas.PositionCreate):
    db_position = models.Position(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position

def update_position(db: Session, position_id: int, position: schemas.PositionUpdate):
    db_position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if db_position:
        update_data = position.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_position, field, value)
        db.commit()
        db.refresh(db_position)
    return db_position

def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note