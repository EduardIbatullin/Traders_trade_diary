from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .. import crud, models, schemas
from ..database import get_db
from ..importer import parse_sber_report
from ..schemas import trade_schemas as schemas

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/trades")
async def import_trades_from_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Импорт сделок из HTML-отчета брокера
    """
    if not file.filename.endswith(('.html', '.htm')):
        raise HTTPException(
            status_code=400,
            detail="Файл должен быть в формате HTML"
        )
    
    try:
        # Читаем содержимое файла
        content = await file.read()
        html_content = content.decode('utf-8')
        
        # Парсим отчет
        parsed_data = parse_sber_report(html_content)
        
        imported_trades = []
        
        # Обрабатываем сделки из отчета
        if 'trades' in parsed_data:
            for trade_data in parsed_data['trades']:
                # Проверяем, существует ли уже сделка с такими параметрами
                existing_trade = db.query(models.Trade).filter(
                    models.Trade.instrument == trade_data['instrument'],
                    models.Trade.trade_date == trade_data['trade_date'],
                    models.Trade.operation == trade_data['operation'],
                    models.Trade.quantity == trade_data['quantity'],
                    models.Trade.price == trade_data['price']
                ).first()
                
                if existing_trade:
                    continue  # Пропускаем дубликаты
                
                # Создаем схему для валидации данных
                trade_schema = schemas.TradeCreate(
                    instrument=trade_data['instrument'],
                    trade_date=trade_data['trade_date'],
                    operation=trade_data['operation'],
                    quantity=trade_data['quantity'],
                    price=trade_data['price'],
                    commission=trade_data['commission']
                )
                
                # Создаем сделку в базе данных
                db_trade = crud.create_trade(db, trade_schema)
                imported_trades.append(db_trade)
        
        return {
            "message": f"Успешно импортировано {len(imported_trades)} сделок",
            "imported_trades": imported_trades
        }
    
    except UnicodeDecodeError:
        # Попробуем другой кодировку
        try:
            content = await file.read()
            html_content = content.decode('cp1251')
            parsed_data = parse_sber_report(html_content)
            
            imported_trades = []
            if 'trades' in parsed_data:
                for trade_data in parsed_data['trades']:
                    existing_trade = db.query(models.Trade).filter(
                        models.Trade.instrument == trade_data['instrument'],
                        models.Trade.trade_date == trade_data['trade_date'],
                        models.Trade.operation == trade_data['operation'],
                        models.Trade.quantity == trade_data['quantity'],
                        models.Trade.price == trade_data['price']
                    ).first()
                    
                    if existing_trade:
                        continue
                    
                    trade_schema = schemas.TradeCreate(
                        instrument=trade_data['instrument'],
                        trade_date=trade_data['trade_date'],
                        operation=trade_data['operation'],
                        quantity=trade_data['quantity'],
                        price=trade_data['price'],
                        commission=trade_data['commission']
                    )
                    
                    db_trade = crud.create_trade(db, trade_schema)
                    imported_trades.append(db_trade)
            
            return {
                "message": f"Успешно импортировано {len(imported_trades)} сделок",
                "imported_trades": imported_trades
            }
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при обработке файла: {str(e)}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при импорте отчета: {str(e)}"
        )


@router.post("/preview")
async def preview_import_from_report(
    file: UploadFile = File(...)
):
    """
    Предварительный просмотр импорта из HTML-отчета
    """
    if not file.filename.endswith(('.html', '.htm')):
        raise HTTPException(
            status_code=400,
            detail="Файл должен быть в формате HTML"
        )
    
    try:
        content = await file.read()
        html_content = content.decode('utf-8')
        
        parsed_data = parse_sber_report(html_content)
        
        # Подсчитываем количество сделок для предпросмотра
        trades_count = len(parsed_data.get('trades', []))
        currency_count = len(parsed_data.get('currency_pairs', []))
        
        return {
            "trades_count": trades_count,
            "currency_operations_count": currency_count,
            "preview_data": parsed_data.get('trades', [])[:10]  # Первые 10 сделок для предпросмотра
        }
    
    except UnicodeDecodeError:
        try:
            content = await file.read()
            html_content = content.decode('cp1251')
            parsed_data = parse_sber_report(html_content)
            
            trades_count = len(parsed_data.get('trades', []))
            currency_count = len(parsed_data.get('currency_pairs', []))
            
            return {
                "trades_count": trades_count,
                "currency_operations_count": currency_count,
                "preview_data": parsed_data.get('trades', [])[:10]
            }
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при обработке файла: {str(e)}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при обработке отчета: {str(e)}"
        )