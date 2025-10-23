import httpx
import asyncio
from typing import Optional, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None

    async def send_message(self, text: str) -> Dict[str, Any]:
        if not self.bot_token or not self.chat_id or not self.base_url:
            logger.warning("Telegram integration is not configured")
            return {"success": False, "error": "Telegram integration not configured"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": "HTML"
                    }
                )
                
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    logger.error(f"Failed to send Telegram message: {response.text}")
                    return {"success": False, "error": response.text}
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return {"success": False, "error": str(e)}

    def format_trade_message(self, trade_data: Dict[str, Any]) -> str:
        """Форматирование информации о сделке в сообщение для Telegram"""
        operation_text = "🟢 КУПЛЯ" if trade_data.get('operation', '').lower() == 'buy' else "🔴 ПРОДАЖА"
        
        message = f"""
📊 <b>НОВАЯ СДЕЛКА</b>

.instrument: {trade_data.get('instrument', 'N/A')}
.operation: {operation_text}
.qty: {trade_data.get('quantity', 'N/A')}
.price: {trade_data.get('price', 'N/A')}
.date: {trade_data.get('trade_date', 'N/A')}
.commission: {trade_data.get('commission', 0)}

📝 <b>Заметка:</b> {trade_data.get('note', 'Нет')}
        """.strip()
        
        return message