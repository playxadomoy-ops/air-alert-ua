import requests

class AlertsApiService:
    def __init__(self):
        self.url = "https://alerts.in.ua"
        self.token = "YOUR_OFFICIAL_ALERTS_IN_UA_TOKEN_HERE"

    def get_region_status(self, region_name="Київська область") -> dict:
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            response = requests.get(self.url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                active_alerts = data.get("alerts", [])

                for alert in active_alerts:
                    location_title = alert.get("location_title", "")
                    if region_name.lower() in location_title.lower():
                        return {
                            "active": True,
                            "type": alert.get("location_type", "Повітряна тривога"),
                            "time": alert.get("started_at", "Невідомо")
                        }
                return {"active": False, "type": "НЕМАЄ ТРИВОГИ", "time": "Щойно"}
            else:
                return {"active": False, "type": f"Помилка API (Код {response.status_code})", "time": "Помилка"}
        except Exception:
            return {"active": False, "type": "Помилка підключення до мережі API тривог", "time": "Помилка"}
