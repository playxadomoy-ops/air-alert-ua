import asyncio
import os
from telethon import TelegramClient, events

KEYWORDS = {
    "міг-31к": 9, "кинжал": 10, "балістика": 9, "ракета": 7, "крилата ракета": 8,
    "каб": 6, "керована авіабомба": 6, "шахед": 5, "shahed": 5, "бпла": 4,
    "вибух": 7, "пуск": 5, "стратегічна авіація": 6, "тривога": 2
}

KYIV_TRIGGERS = [
    "київ", "киів", "київщ", "київськ", "васильк", "бровар", "борисп", "обух",
    "ірпін", "буч", "вишг", "біла церк", "фастів", "переяслав", "яготин"
]

async def start_telegram_logic(api_id, api_hash, settings_data, update_ui_callback, data_dir=None):
    target_channels = [settings_data[k].strip() for k in ["channel1", "channel2", "channel3"] if settings_data[k].strip()]
    if not target_channels:
        return

    try:
        base_dir = data_dir if data_dir else os.getcwd()
        # Сесія користувача (UserBot)
        session_path = os.path.join(base_dir, 'user_monitor_session')

        loop = asyncio.get_running_loop()
        client = TelegramClient(session_path, api_id, api_hash, loop=loop)

        @client.on(events.NewMessage(chats=target_channels))
        async def handler(event):
            try:
                msg_text = event.message.message or ""
                if not msg_text:
                    return

                text_lower = msg_text.lower()
                max_risk = 0
                detected_danger = "Чисте небо"

                if "відбій" in text_lower or "чисто" in text_lower:
                    if "київ" in text_lower or "київщ" in text_lower or len(text_lower) < 40:
                        update_ui_callback(0, "чисте небо", msg_text)
                        return

                is_for_kyiv = any(trigger in text_lower for trigger in KYIV_TRIGGERS) or any(
                    w in text_lower for w in ["міг-31к", "ту-95", "крилаті ракети"])
                if not is_for_kyiv:
                    return

                for word, weight in KEYWORDS.items():
                    if word in text_lower and weight > max_risk:
                        max_risk = weight
                        detected_danger = word

                update_ui_callback(max_risk, detected_danger, msg_text)
            except Exception as e:
                print(f"Помилка обробки повідомлення: {e}")

        # Метод client.start() без bot_token автоматично запросить номер телефону та код у консолі!
        await client.start()
        print("🤖 Юзербот успішно авторизований та запущений!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Помилка фонового клієнта: {e}")
