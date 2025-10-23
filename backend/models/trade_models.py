from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String, index=True, nullable=False)
    trade_date = Column(DateTime, nullable=False)
    operation = Column(String, nullable=False)  # 'buy' или 'sell'
    quantity = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    commission = Column(Numeric, default=0)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    note = relationship("Note", back_populates="trade")
    position = relationship("Position", back_populates="trades")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    instrument = Column(String, index=True, nullable=False)
    avg_price = Column(Numeric)
    quantity_total = Column(Numeric)
    total_commission = Column(Numeric)
    total_profit_loss_value = Column(Numeric)
    total_profit_loss_percent = Column(Numeric)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    note = relationship("Note", back_populates="position")
    trades = relationship("Trade", back_populates="position")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    trade = relationship("Trade", back_populates="note", uselist=False)
    position = relationship("Position", back_populates="note", uselist=False)