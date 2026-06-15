import flet as ft
import asyncio
import os
import json
import datetime
import newmain2  # Логічний модуль

# Дані з сайту my.telegram.org (залишаються твої)
API_ID = 34142195
API_HASH = '2c2fe5dd3aeb60f62859c2e103825bda'


def main(page: ft.Page):
    page.title = "AI Монітор ТРИВОГ"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121316"
    page.padding = 20
    page.scroll = "adaptive"

    settings_file = os.path.join(os.getcwd(), "mobile_settings.json")
    data_dir = os.getcwd()

    def load_settings():
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"channel1": "@povitryana_tryvoga_ua", "channel2": "@Nashee_PPO", "channel3": "@cheste_nebo"}

    settings_data = load_settings()

    # --- ЕЛЕМЕНТИ ІНТЕРФЕЙСУ ---
    notification_text = ft.Text("Очікування нових сповіщень...", size=13, color="#e0e0e0")
    risk_time_text = ft.Text("00:00:00", size=32, weight=ft.FontWeight.BOLD, color="#22c55e", text_align="center")
    status_text = ft.Text("чисте небо", size=14, color="#a1a1aa", text_align="center")

    ch1_label = ft.Text(settings_data["channel1"], size=13, color="#e0e0e0")
    ch2_label = ft.Text(settings_data["channel2"], size=13, color="#e0e0e0")
    ch3_label = ft.Text(settings_data["channel3"], size=13, color="#e0e0e0")

    bot1_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor="#22c55e")
    bot2_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor="#22c55e")
    bot3_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor="#22c55e")

    map_status_label = ft.Text("КИЇВЩИНА: НЕБО ЧИСТЕ", size=14, weight=ft.FontWeight.BOLD, color="#22c55e")

    # Використовуємо локальну карту, якщо завантажиш. Якщо ні — буде порожній контейнер замість помилки
    map_image = ft.Image(
        src="map_bg.png" if os.path.exists("map_bg.png") else "",
        width=280,
        height=160,
        fit="contain",
        color="#22c55e",
    )

    map_container = ft.Container(
        content=ft.Column([
            map_image,
            map_status_label
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        padding=10
    )

    current_risk = 0

    async def update_clock():
        while True:
            if current_risk == 0:
                now = datetime.datetime.now().strftime("%H:%M:%S")
                risk_time_text.value = now
                risk_time_text.color = "#22c55e"
                status_text.value = "чисте небо"
                status_text.color = "#a1a1aa"
                map_status_label.value = "КИЇВЩИНА: НЕБО ЧИСТЕ"
                map_status_label.color = "#22c55e"
                map_image.color = "#22c55e"
            page.update()
            await asyncio.sleep(1)

    def send_mobile_notification(title, text):
        notification_text.value = text
        page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{title}: {text}"), bgcolor="#1a1b20"))
        page.update()

    def update_ui_from_worker(risk_val, danger_text, raw_text):
        nonlocal current_risk
        current_risk = risk_val

        if risk_val > 0:
            risk_time_text.value = f"РИЗИК: {risk_val}/10"
            status_text.value = danger_text.lower()
            color = "#ff3333" if risk_val > 4 else "#eab308"

            bot1_dot.bgcolor = color
            bot2_dot.bgcolor = color
            bot3_dot.bgcolor = color
            risk_time_text.color = color
            status_text.color = color

            map_image.color = color
            map_status_label.value = f"ТРИВОГА! {danger_text.upper()}"
            map_status_label.color = color

            send_mobile_notification("⚠️ ЗАГРОЗА КИЇВЩИНА", raw_text)
        else:
            bot1_dot.bgcolor = "#22c55e"
            bot2_dot.bgcolor = "#22c55e"
            bot3_dot.bgcolor = "#22c55e"
            map_image.color = "#22c55e"
            map_status_label.value = "КИЇВЩИНА: НЕБО ЧИСТЕ"
            map_status_label.color = "#22c55e"
            send_mobile_notification("🟢 ВІДБІЙ ТРИВОГИ", "Київська область: небо чисте.")
        page.update()

    ch1_input = ft.TextField(label="Канал 1", value=settings_data["channel1"], bgcolor="#1e1f24")
    ch2_input = ft.TextField(label="Канал 2", value=settings_data["channel2"], bgcolor="#1e1f24")
    ch3_input = ft.TextField(label="Канал 3", value=settings_data["channel3"], bgcolor="#1e1f24")

    def save_settings_click(e):
        settings_data["channel1"] = ch1_input.value.strip()
        settings_data["channel2"] = ch2_input.value.strip()
        settings_data["channel3"] = ch3_input.value.strip()
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)

        ch1_label.value = settings_data["channel1"]
        ch2_label.value = settings_data["channel2"]
        ch3_label.value = settings_data["channel3"]
        page.banner.open = False
        page.update()

    def open_settings(e):
        page.banner = ft.Banner(
            bgcolor="#1a1b20", leading=ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.BLUE),
            content=ft.Column(
                [ft.Text("Редагування каналів:", weight=ft.FontWeight.BOLD), ch1_input, ch2_input, ch3_input],
                spacing=10
            ),
            actions=[
                ft.TextButton("Зберегти", on_click=save_settings_click),
                ft.TextButton("Скасувати", on_click=lambda _: setattr(page.banner, 'open', False) or page.update())
            ]
        )
        page.banner.open = True
        page.update()

    # --- ВЕРСТКА ---
    header_block = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color="#ffffff"),
                        ft.Text("сповіщення", size=18, color="#ffffff")], spacing=10),
                ft.IconButton(ft.Icons.SETTINGS_OUTLINED, icon_color="#ffffff", on_click=open_settings)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(content=notification_text, padding=5)
        ]), padding=15, bgcolor="#1a1b20", border_radius=15
    )

    alarm_block = ft.Container(
        content=ft.Column([
            ft.Text("ризик тривог / час", size=14, color="#a1a1aa"),
            ft.Row([
                ft.Container(
                    content=ft.Column([risk_time_text, status_text], alignment=ft.MainAxisAlignment.CENTER,
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor="#121316", width=160, height=100, border_radius=12
                ),
                ft.Column([
                    ft.Row([bot1_dot, ch1_label], spacing=8),
                    ft.Row([bot2_dot, ch2_label], spacing=8),
                    ft.Row([bot3_dot, ch3_label], spacing=8),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]), padding=15, bgcolor="#1a1b20", border_radius=15
    )

    tg_channels_block = ft.Container(
        content=ft.Row([ft.Text("Акаунт Telegram: підключено", size=16, color="#ffffff", weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.PERSON, color="#229ED9", size=20)],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=15, bgcolor="#1a1b20", border_radius=15
    )

    map_block = ft.Container(
        content=ft.Column([
            ft.Text("карта ризику тривог", size=16, color="#ffffff"),
            ft.Row([map_container], alignment=ft.MainAxisAlignment.CENTER)
        ]), padding=15, bgcolor="#1a1b20", border_radius=15
    )

    page.add(ft.Column([header_block, alarm_block, tg_channels_block, map_block], spacing=15))

    async def launch_telegram():
        await newmain2.start_telegram_logic(
            api_id=API_ID,
            api_hash=API_HASH,
            settings_data=settings_data,
            update_ui_callback=update_ui_from_worker,
            data_dir=data_dir
        )

    page.run_task(update_clock)
    page.run_task(launch_telegram)


if __name__ == "__main__":
    ft.run(main)
