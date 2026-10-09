# bot.py - Complete TikTok Live Treasure Chest Monitor & Telegram Bot
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import EnvelopeEvent, ConnectEvent, DisconnectEvent

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

MONITORED_CREATORS = ["streamer_username_1"]

async def send_telegram_alert(streamer_id: str, box_info: str):
    url = f"https://www.tiktok.com/@{streamer_id}/live"
    message = (
        f"🚨 **PHÁT HIỆN RƯƠNG XU TIKTOK!** 🚨\n\n"
        f"👤 Kênh: `@{streamer_id}`\n"
        f"📦 Thông tin: {box_info}\n"
        f"🔗 [VÀO XEM NGAY]({url})"
    )
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

async def monitor_streamer(unique_id: str):
    client: TikTokLiveClient = TikTokLiveClient(unique_id=f"@{unique_id}")
    
    @client.on(EnvelopeEvent)
    async def on_envelope(event: EnvelopeEvent):
        box_data = str(event.treasureBoxData) if hasattr(event, 'treasureBoxData') else "Rương xu sắp mở"
        await send_telegram_alert(unique_id, box_data)

    @client.on(DisconnectEvent)
    async def on_disconnect(event: DisconnectEvent):
        await asyncio.sleep(30)
        try:
            await client.start()
        except Exception:
            pass

    while True:
        try:
            await client.start()
        except Exception:
            await asyncio.sleep(15)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **TikTok Live Treasure Bot** đang hoạt động, boss man!")

async def main():
    monitor_tasks = [asyncio.create_task(monitor_streamer(creator)) for creator in MONITORED_CREATORS]
    await dp.start_polling(bot)
    for task in monitor_tasks:
        task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
