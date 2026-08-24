class TaskDisplay:

    def __init__(self, screen):
        self.screen = screen

    def format_date(self, value):
        if not value:
            return "-"

        if len(value) >= 8:
            return (
                value[6:8]
                + "."
                + value[4:6]
                + "."
                + value[0:4]
            )

        return value

    def draw_task(self, task, y, level=0):

        lcd = self.screen

        name = task.get("summary", "Ohne Namen")
        due = self.format_date(
            task.get("due", "") or task.get("end", "")
        )
        calendar = task.get("calendar", "-")

        x = 5 + (level * 12)

        # Aufgabenname
        lcd.text(
            name[:35],
            x,
            y,
            lcd.WHITE
        )

        # Fälligkeitsdatum
        lcd.text(
            due,
            x,
            y + 15,
            lcd.WHITE
        )



        y += 38

        # Unteraufgaben
        children = task.get("children", [])

        for child in children:

            if y >= lcd.height:
                break

            y = self.draw_task(
                child,
                y,
                level + 1
            )

        return y

    def show_tasks(self, tasks):

        lcd = self.screen

        lcd.fill(lcd.BLACK)

        y = 5

        for task in tasks:

            if y >= lcd.height:
                break

            y = self.draw_task(
                task,
                y
            )

        lcd.show_down()
