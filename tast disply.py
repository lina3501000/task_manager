class TaskDisplay:

    def __init__(self, screen):
        self.screen = screen

    def format_date(self, value):
        if not value:
            return "-"

        # YYYYMMDD
        if len(value) >= 8:
            return value[6:8] + "." + value[4:6] + "." + value[0:4]

        return value

    def show_tasks(self, tasks):

        lcd = self.screen

        lcd.fill(lcd.BLACK)

        y = 5

        for task in tasks:

            name = task.get("summary", "Ohne Namen")
            start = self.format_date(task.get("start", ""))
            end = self.format_date(
                task.get("end", "") or task.get("due", "")
            )
            calendar = task.get("calendar", "-")

            # Aufgabenname
            lcd.text(
                name[:45],
                5,
                y,
                lcd.WHITE
            )

            # Informationen darunter
            lcd.text(
                start,
                5,
                y + 15,
                lcd.WHITE
            )

            lcd.text(
                end,
                85,
                y + 15,
                lcd.WHITE
            )

            lcd.text(
                calendar[:20],
                165,
                y + 15,
                lcd.WHITE
            )

            y += 38

            if y >= lcd.height:
                break

        lcd.show_down()
