"""
Модуль для расчетов, связанных с позициями и сделками
"""

from decimal import Decimal
from typing import List, Optional
from backend.models.trade_models import Trade, Position
from datetime import datetime


def calculate_average_price(trades: List[Trade]) -> Optional[Decimal]:
    """
    Рассчитывает среднюю цену позиции на основе списка сделок.
    
    :param trades: Список сделок для расчета
    :return: Средняя цена или None, если нет сделок
    """
    if not trades:
        return None
    
    total_quantity = Decimal('0')
    total_cost = Decimal('0')
    
    for trade in trades:
        quantity = Decimal(str(trade.quantity))
        price = Decimal(str(trade.price))
        commission = Decimal(str(trade.commission or 0))
        
        if trade.operation.lower() == 'buy':
            total_quantity += quantity
            total_cost += (quantity * price) + commission
        elif trade.operation.lower() == 'sell':
            # Для расчета средней цены продажи вычитаются из общей стоимости и количества
            total_quantity -= quantity
            total_cost -= (quantity * price) - commission  # При продаже мы "возвращаем" деньги за вычетом комиссии
    
    if total_quantity <= 0:
        return None
    
    return total_cost / total_quantity


def calculate_position_pnl(trades: List[Trade], current_price: Decimal) -> dict:
    """
    Рассчитывает прибыль/убыток для позиции.
    
    :param trades: Список сделок для расчета
    :param current_price: Текущая рыночная цена инструмента
    :return: Словарь с результатами расчетов
    """
    if not trades:
        return {
            'total_profit_loss_value': Decimal('0'),
            'total_profit_loss_percent': Decimal('0'),
            'quantity_held': Decimal('0'),
            'avg_price': None
        }
    
    avg_price = calculate_average_price(trades)
    if avg_price is None:
        return {
            'total_profit_loss_value': Decimal('0'),
            'total_profit_loss_percent': Decimal('0'),
            'quantity_held': Decimal('0'),
            'avg_price': None
        }
    
    # Подсчитываем количество удерживаемых акций
    quantity_held = Decimal('0')
    total_commission = Decimal('0')
    
    for trade in trades:
        quantity = Decimal(str(trade.quantity))
        commission = Decimal(str(trade.commission or 0))
        total_commission += commission
        
        if trade.operation.lower() == 'buy':
            quantity_held += quantity
        elif trade.operation.lower() == 'sell':
            quantity_held -= quantity
    
    if quantity_held <= 0:
        return {
            'total_profit_loss_value': Decimal('0'),
            'total_profit_loss_percent': Decimal('0'),
            'quantity_held': quantity_held,
            'avg_price': avg_price
        }
    
    # Рассчитываем текущую прибыль/убыток
    current_value = quantity_held * current_price
    cost_basis = quantity_held * avg_price
    profit_loss_value = current_value - cost_basis
    
    # Рассчитываем процент прибыли/убытка
    if cost_basis != 0:
        profit_loss_percent = (profit_loss_value / cost_basis) * 100
    else:
        profit_loss_percent = Decimal('0')
    
    return {
        'total_profit_loss_value': profit_loss_value,
        'total_profit_loss_percent': profit_loss_percent,
        'quantity_held': quantity_held,
        'avg_price': avg_price,
        'total_commission': total_commission
    }


def calculate_trade_pnl(trade: Trade, exit_price: Decimal) -> dict:
    """
    Рассчитывает прибыль/убыток для конкретной сделки на продажу.
    
    :param trade: Сделка покупки (для которой рассчитываем P/L при продаже)
    :param exit_price: Цена продажи
    :return: Словарь с результатами расчетов
    """
    quantity = Decimal(str(trade.quantity))
    entry_price = Decimal(str(trade.price))
    commission_entry = Decimal(str(trade.commission or 0))
    commission_exit = Decimal('0')  # Пока предполагаем, что комиссия на продажу неизвестна
    
    entry_cost = (quantity * entry_price) + commission_entry
    exit_value = (quantity * exit_price) - commission_exit
    profit_loss_value = exit_value - entry_cost
    
    if entry_cost != 0:
        profit_loss_percent = (profit_loss_value / entry_cost) * 100
    else:
        profit_loss_percent = Decimal('0')
    
    return {
        'profit_loss_value': profit_loss_value,
        'profit_loss_percent': profit_loss_percent
    }