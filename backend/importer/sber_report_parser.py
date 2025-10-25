"""
Модуль для импорта HTML-отчетов брокера Сбер
"""
from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
import re
from bs4 import BeautifulSoup
from backend.models.trade_models import Trade
from backend.schemas import trade_schemas as schemas


class SberBankReportParser:
    """
    Парсер HTML-отчетов брокера Сбер
    Поддерживает суточные и месячные отчеты
    """
    
    def __init__(self):
        self.supported_tables = [
            "Сделки",  # Основная таблица с торговыми операциями
            "Валютные пары",  # Если отчет содержит валютные операции
        ]
    
    def parse_report(self, html_content: str) -> Dict[str, List]:
        """
        Основная функция для парсинга HTML-отчета
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = {}
        
        # Находим все таблицы в отчете
        tables = soup.find_all('table')
        
        for table in tables:
            # Определяем тип таблицы
            table_name = self._get_table_name(table)
            
            if table_name == "Сделки":
                results['trades'] = self._parse_trades_table(table)
            elif table_name == "Валютные пары":
                results['currency_pairs'] = self._parse_currency_table(table)
        
        return results

    def _get_table_name(self, table) -> str:
        """
        Определяет тип таблицы по заголовкам
        """
        # Ищем заголовок таблицы выше самой таблицы
        prev_sibling = table.find_previous_sibling()
        if prev_sibling and prev_sibling.name == 'p':
            text = prev_sibling.get_text(strip=True)
            if 'сделки' in text.lower():
                return "Сделки"
            elif 'валютные' in text.lower() or 'currency' in text.lower():
                return "Валютные пары"
        
        # Ищем заголовок в самой таблице (обычно в первом ряду)
        first_row = table.find('tr')
        if first_row:
            cells = first_row.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text(strip=True)
                if 'сделки' in text.lower():
                    return "Сделки"
                elif 'валютные' in text.lower():
                    return "Валютные пары"
        
        # Если не нашли название, пробуем определить по столбцам
        headers = self._get_table_headers(table)
        if headers:
            if any('инструмент' in h.lower() or 'ticker' in h.lower() for h in headers):
                if any('цена' in h.lower() or 'price' in h.lower() for h in headers):
                    return "Сделки"
        
        return "Неизвестная таблица"

    def _get_table_headers(self, table) -> List[str]:
        """
        Получает названия столбцов таблицы
        """
        headers = []
        header_row = table.find('tr')  # Обычно первый ряд содержит заголовки
        if header_row:
            cells = header_row.find_all(['th', 'td'])
            for cell in cells:
                headers.append(cell.get_text(strip=True))
        return headers

    def _parse_trades_table(self, table) -> List[Dict]:
        """
        Парсит таблицу с торговыми операциями
        """
        trades = []
        rows = table.find_all('tr')[1:]  # Пропускаем заголовок
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 5:  # Минимум 5 столбцов для сделки
                continue
            
            try:
                trade_data = self._parse_trade_row(cells)
                if trade_data:
                    trades.append(trade_data)
            except Exception as e:
                print(f"Ошибка при парсинге строки сделки: {e}")
                continue
        
        return trades

    def _parse_trade_row(self, cells) -> Optional[Dict]:
        """
        Парсит одну строку таблицы сделок
        """
        # В типичном отчете Сбербанка:
        # 0 - Номер
        # 1 - Дата и время
        # 2 - Тикер/инструмент
        # 3 - Вид операции (покупка/продажа)
        # 4 - Количество
        # 5 - Цена
        # 6 - Сумма
        # 7 - Комиссия
        
        if len(cells) < 8:
            return None
        
        # Обработка даты и времени
        date_time_str = cells[1].get_text(strip=True)
        trade_datetime = self._parse_datetime(date_time_str)
        if not trade_datetime:
            return None
        
        # Обработка инструмента
        instrument = cells[2].get_text(strip=True).strip()
        
        # Обработка операции
        operation_raw = cells[3].get_text(strip=True).strip()
        operation = self._parse_operation(operation_raw)
        if not operation:
            return None
        
        # Обработка количества
        quantity_raw = re.sub(r'[^\d.,-]', '', cells[4].get_text(strip=True))
        try:
            quantity = float(quantity_raw.replace(',', '.'))
        except ValueError:
            quantity = 0
        
        # Обработка цены
        price_raw = re.sub(r'[^\d.,-]', '', cells[5].get_text(strip=True))
        try:
            price = float(price_raw.replace(',', '.'))
        except ValueError:
            price = 0
        
        # Обработка комиссии
        commission_raw = re.sub(r'[^\d.,-]', '', cells[7].get_text(strip=True))
        try:
            commission = float(commission_raw.replace(',', '.'))
        except ValueError:
            commission = 0
        
        return {
            'instrument': instrument,
            'trade_date': trade_datetime,
            'operation': operation,
            'quantity': quantity,
            'price': price,
            'commission': commission
        }

    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        Парсит дату и время из строкового представления
        Поддерживает несколько форматов, используемых в отчетах Сбербанка
        """
        if not datetime_str:
            return None
        
        # Очищаем строку от лишних символов
        datetime_str = datetime_str.strip()
        
        # Пробуем несколько форматов
        formats = [
            "%d.%m.%Y %H:%M:%S",  # 15.08.2024 10:15:30
            "%d.%m.%Y %H:%M",     # 15.08.2024 10:15
            "%Y-%m-%d %H:%M:%S",  # 2024-08-15 10:15:30
            "%Y-%m-%d %H:%M",     # 2024-08-15 10:15
            "%d.%m.%Y",           # 15.08.2024
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        # Если ни один формат не подошел, возвращаем None
        return None

    def _parse_operation(self, operation_str: str) -> Optional[str]:
        """
        Парсит тип операции (покупка/продажа)
        """
        if not operation_str:
            return None
        
        operation_str = operation_str.lower().strip()
        
        # Покупка
        if any(buy_word in operation_str for buy_word in ['покупка', 'buy', 'long']):
            return 'buy'
        
        # Продажа
        elif any(sell_word in operation_str for sell_word in ['продажа', 'sell', 'short']):
            return 'sell'
        
        # Неизвестная операция
        else:
            return None

    def _parse_currency_table(self, table) -> List[Dict]:
        """
        Парсит таблицу с валютными операциями
        """
        # Реализация будет аналогичной _parse_trades_table
        # но с учетом специфики валютных операций
        currencies = []
        rows = table.find_all('tr')[1:]  # Пропускаем заголовок
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # Минимум 3 столбца
                continue
            
            # Обработка конкретной строки с валютной операцией
            # Пока что оставляем как заглушку
            currency_data = {
                'currency_pair': cells[0].get_text(strip=True),
                'amount': cells[1].get_text(strip=True),
                'rate': cells[2].get_text(strip=True)
            }
            currencies.append(currency_data)
        
        return currencies

    def validate_report_format(self, html_content: str) -> bool:
        """
        Проверяет, является ли HTML-контент отчетом Сбербанка
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Ищем характерные признаки отчета Сбербанка
        title = soup.find('title')
        if title and 'сбер' in title.get_text().lower():
            return True
        
        # Ищем упоминание Сбербанка в документе
        text = soup.get_text()
        if 'сбербанк' in text.lower() or 'sberbank' in text.lower():
            return True
        
        # Проверяем наличие типичных таблиц
        tables = soup.find_all('table')
        for table in tables:
            table_name = self._get_table_name(table)
            if table_name in self.supported_tables:
                return True
        
        return False


# Функция для удобного использования
def parse_sber_report(html_content: str) -> Dict[str, List]:
    """
    Функция высокого уровня для парсинга отчета Сбербанка
    """
    parser = SberBankReportParser()
    
    if not parser.validate_report_format(html_content):
        raise ValueError("Формат отчета не соответствует ожидаемому")
    
    return parser.parse_report(html_content)