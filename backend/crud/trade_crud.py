from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from . import models, schemas
from ..calculations import calculate_average_price, calculate_position_pnl

def get_trade(db: Session, trade_id: int):
    return db.query(models.Trade).filter(models.Trade.id == trade_id).first()

def get_trades(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Trade).offset(skip).limit(limit).all()

def create_trade(db: Session, trade: schemas.TradeCreate):
    db_trade = models.Trade(**trade.model_dump())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    # Обновляем связанную позицию при необходимости
    update_position_after_trade(db, db_trade)
    
    return db_trade

def update_trade(db: Session, trade_id: int, trade: schemas.TradeUpdate):
    db_trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()
    if db_trade:
        update_data = trade.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_trade, field, value)
        db.commit()
        db.refresh(db_trade)
        
        # Обновляем связанную позицию при необходимости
        update_position_after_trade(db, db_trade)
        
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
    positions = db.query(models.Position).offset(skip).limit(limit).all()
    
    # Добавляем расчеты для каждой позиции
    for position in positions:
        trades = db.query(models.Trade).filter(
            models.Trade.instrument == position.instrument
        ).all()
        
        if trades:
            # Используем расчеты для обогащения данных позиции
            avg_price = calculate_average_price(trades)
            if avg_price:
                position.avg_price = float(avg_price)
    
    return positions

def create_position(db: Session, position: schemas.PositionCreate):
    db_position = models.Position(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    
    # Обновляем позицию с рассчитанными значениями
    update_position_calculations(db, db_position.id)
    
    return db_position

def update_position(db: Session, position_id: int, position: schemas.PositionUpdate):
    db_position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if db_position:
        update_data = position.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_position, field, value)
        db.commit()
        db.refresh(db_position)
        
        # Обновляем позицию с рассчитанными значениями
        update_position_calculations(db, position_id)
        
    return db_position

def get_position_by_id(db: Session, position_id: int):
    position = db.query(models.Position).filter(models.Position.id == position_id).first()
    
    if position:
        # Рассчитываем и обновляем данные позиции
        update_position_calculations(db, position_id)
    
    return position

def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_position(db: Session, position_id: int):
    db_position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if db_position:
        db.delete(db_position)
        db.commit()
        return True
    return False

def get_trades_by_instrument(db: Session, instrument: str):
    """Получить все сделки по инструменту для расчетов"""
    return db.query(models.Trade).filter(models.Trade.instrument == instrument).all()

def update_position_after_trade(db: Session, trade: models.Trade):
    """Обновить позицию после создания/обновления сделки"""
    # Находим или создаем позицию для инструмента
    position = db.query(models.Position).filter(
        models.Position.instrument == trade.instrument
    ).first()
    
    if not position:
        # Создаем новую позицию, если не существует
        position = models.Position(
            instrument=trade.instrument
        )
        db.add(position)
        db.commit()
        db.refresh(position)
    
    # Обновляем позицию с рассчитанными значениями
    update_position_calculations(db, position.id)

def update_position_calculations(db: Session, position_id: int):
    """Обновить позицию с рассчитанными значениями"""
    position = db.query(models.Position).filter(models.Position.id == position_id).first()
    if not position:
        return position
    
    # Получаем все сделки по этому инструменту
    trades = get_trades_by_instrument(db, position.instrument)
    
    if trades:
        # Рассчитываем среднюю цену и P/L
        avg_price = calculate_average_price(trades)
        if avg_price:
            position.avg_price = float(avg_price)
        
        # Для простоты в MVP используем условную текущую цену,
        # в дальнейшем будет интеграция с API котировок
        # Пока просто рассчитываем на основе последней сделки
        last_trade = trades[-1]
        current_price = Decimal(str(last_trade.price))
        
        pnl_data = calculate_position_pnl(trades, current_price)
        
        position.quantity_total = float(pnl_data['quantity_held'])
        position.total_commission = float(pnl_data.get('total_commission', 0))
        position.total_profit_loss_value = float(pnl_data['total_profit_loss_value'])
        position.total_profit_loss_percent = float(pnl_data['total_profit_loss_percent'])
        
        db.commit()
        db.refresh(position)
    
    return position