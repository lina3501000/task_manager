import time
import framebuf


class TaskDisplay:

    def __init__(self, screen):
        self.screen = screen

        # Darstellung
        self.row_height = 75

        self.page = 0
        self.tasks = []
        self.flat_tasks = []

        # --------------------------------------------------
        # MANUELLE TOUCH-BEREICHE
        #
        # [untere Grenze, obere Grenze]
        #
        # Roh-X-Wert des Touchscreens!
        # --------------------------------------------------

        self.touch_areas = [
            [400, 475],   # Aufgabe 1
            [340, 380],   # Aufgabe 2
            [265, 330],   # Aufgabe 3
            [195, 240],   # Aufgabe 4
            [110, 165],   # Aufgabe 5
            [0,   80]     # Weiter
        ]


    # --------------------------------------------------
    # Datum formatieren
    # --------------------------------------------------

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


    # --------------------------------------------------
    # Aufgaben inklusive Unteraufgaben flach machen
    # --------------------------------------------------

    def flatten_tasks(self, tasks):

        result = []

        def add_tasks(task_list, level=0):

            for task in task_list:

                result.append(
                    (task, level)
                )

                children = task.get(
                    "children",
                    []
                )

                if children:
                    add_tasks(
                        children,
                        level + 1
                    )

        add_tasks(tasks)

        return result


    # --------------------------------------------------
    # Großen Text zeichnen
    # --------------------------------------------------

    def big_text(self, text, x, y, color):

        width = len(text) * 8
        height = 8

        buffer = bytearray(
            width * height // 8
        )

        fb = framebuf.FrameBuffer(
            buffer,
            width,
            height,
            framebuf.MONO_HLSB
        )

        fb.fill(0)
        fb.text(text, 0, 0, 1)

        for py in range(height):

            for px in range(width):

                if fb.pixel(px, py):

                    self.screen.fill_rect(
                        x + px * 2,
                        y + py * 2,
                        2,
                        2,
                        color
                    )


    # --------------------------------------------------
    # Touch-Bereich bestimmen
    # --------------------------------------------------

    def get_touch_area(self):

        values = []

        # Mehrere Messungen nehmen,
        # damit einzelne Sprünge weniger Einfluss haben.
        for _ in range(5):

            touch = self.screen.touch_get()

            if touch is not None:
                values.append(touch[0])

            time.sleep_ms(10)

        if not values:
            return None

        # Mittelwert der Roh-X-Werte
        raw_x = sum(values) // len(values)

        print(
            "Rohwerte:",
            values,
            "Mittelwert:",
            raw_x
        )

        # Manuelle Bereiche prüfen
        for i, area in enumerate(self.touch_areas):

            lower = area[0]
            upper = area[1]

            if lower <= raw_x <= upper:
                return i + 1

        return None


    # --------------------------------------------------
    # Bildschirm zeichnen
    # --------------------------------------------------

    def draw(self):

        lcd = self.screen

        lcd.fill(lcd.BLACK)

        # --------------------------------------------------
        # Aufgaben dieser Seite
        # --------------------------------------------------

        available_height = (
            lcd.height - self.row_height
        )

        rows_per_page = (
            available_height // self.row_height
        )

        if rows_per_page <= 0:
            rows_per_page = 1

        start = (
            self.page * rows_per_page
        )

        end = min(
            start + rows_per_page,
            len(self.flat_tasks)
        )

        y = 0

        for index in range(start, end):

            task, level = self.flat_tasks[index]

            name = task.get(
                "summary",
                "Ohne Namen"
            )

            due = self.format_date(
                task.get("due", "")
                or task.get("end", "")
            )

            # Unteraufgaben einrücken
            x = 8 + level * 15

            # Aufgabenname groß
            self.big_text(
                name[:22],
                x,
                y + 8,
                lcd.WHITE
            )

            # Fälligkeitsdatum
            lcd.text(
                due,
                x,
                y + 48,
                lcd.WHITE
            )

            # Trennlinie
            if y + self.row_height - 2 < lcd.height:
                lcd.fill_rect(
                    0,
                    y + self.row_height - 2,
                    lcd.width,
                    2,
                    lcd.WHITE
                )

            y += self.row_height


        # --------------------------------------------------
        # Weiter-Button
        # --------------------------------------------------

        button_y = (
            lcd.height - self.row_height
        )

        lcd.fill_rect(
            0,
            button_y,
            lcd.width,
            self.row_height,
            lcd.WHITE
        )

        lcd.text(
            "WEITER",
            130,
            button_y + 30,
            lcd.BLACK
        )

        lcd.show_down()


    # --------------------------------------------------
    # Aufgaben anzeigen
    # --------------------------------------------------

    def show_tasks(self, tasks):

        self.tasks = tasks

        self.flat_tasks = (
            self.flatten_tasks(tasks)
        )

        self.page = 0

        self.draw()

        while True:

            area = self.get_touch_area()

            if area is None:

                time.sleep_ms(50)

                continue


            # --------------------------------------------------
            # Aufgabe 1-5
            # --------------------------------------------------

            if area <= 5:

                available_height = (
                    self.screen.height
                    - self.row_height
                )

                rows_per_page = (
                    available_height
                    // self.row_height
                )

                if rows_per_page <= 0:
                    rows_per_page = 1

                row = area - 1

                index = (
                    self.page
                    * rows_per_page
                    + row
                )

                if index >= len(self.flat_tasks):

                    # Auf dieser Position
                    # gibt es keine Aufgabe.
                    continue

                task, level = (
                    self.flat_tasks[index]
                )

                print(
                    "Aufgabe ausgewählt:",
                    task.get(
                        "summary",
                        ""
                    )
                )


                # --------------------------------------------------
                # Aufgabe erledigen
                # --------------------------------------------------

                try:

                    from caldav import complete_task

                    success = complete_task(task)

                except Exception as e:

                    print(
                        "Fehler beim Erledigen:",
                        e
                    )

                    success = False


                if success:

                    # Wenn Hauptaufgabe erledigt wird,
                    # auch alle Unteraufgaben erledigen.
                    children = task.get(
                        "children",
                        []
                    )

                    for child in children:

                        try:

                            complete_task(child)

                        except Exception as e:

                            print(
                                "Fehler bei Unteraufgabe:",
                                e
                            )


                    # Aufgabe aus Anzeige entfernen
                    self.flat_tasks.pop(index)


                    # Seite ggf. korrigieren
                    page_count = max(
                        1,
                        (
                            len(self.flat_tasks)
                            + rows_per_page
                            - 1
                        )
                        // rows_per_page
                    )

                    if self.page >= page_count:

                        self.page = (
                            page_count - 1
                        )


                    self.draw()


            # --------------------------------------------------
            # Weiter
            # --------------------------------------------------

            elif area == 6:

                available_height = (
                    self.screen.height
                    - self.row_height
                )

                rows_per_page = (
                    available_height
                    // self.row_height
                )

                if rows_per_page <= 0:
                    rows_per_page = 1

                page_count = max(
                    1,
                    (
                        len(self.flat_tasks)
                        + rows_per_page
                        - 1
                    )
                    // rows_per_page
                )

                self.page += 1

                if self.page >= page_count:
                    self.page = 0

                self.draw()


            # --------------------------------------------------
            # Warten bis Finger losgelassen
            # --------------------------------------------------

            while self.screen.touch_get() is not None:

                time.sleep_ms(30)

            time.sleep_ms(200)
