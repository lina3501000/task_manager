import gc
import time


class CalendarScreen:

    def __init__(self, lcd):

        self.lcd = lcd

        self.WHITE = lcd.WHITE
        self.BLACK = lcd.BLACK

    # --------------------------------------------------
    # Datum formatieren
    # --------------------------------------------------

    def format_date(self, value):

        if not value:
            return "-"

        # YYYYMMDD
        if len(value) >= 8:

            year = value[0:4]
            month = value[4:6]
            day = value[6:8]

            result = day + "." + month + "." + year

            # Uhrzeit vorhanden?
            if "T" in value:

                time_part = value.split("T", 1)[1]

                if len(time_part) >= 6:

                    hour = time_part[0:2]
                    minute = time_part[2:4]

                    result += " " + hour + ":" + minute

            return result

        return value

    # --------------------------------------------------
    # Eintrag zeichnen
    # --------------------------------------------------

    def draw_entry(self, entry, number):

        # Jede Aufgabe bekommt 40 Pixel Höhe
        page = number

        if page >= 4:
            return

        def draw(fb):

            title = entry.get("summary", "Ohne Titel")
            calendar = entry.get("calendar", "")

            start = entry.get("start", "")
            end = entry.get("end", "")

            # Titel
            fb.text(
                title[:55],
                5,
                2,
                self.WHITE
            )

            # Kalender
            fb.text(
                calendar[:30],
                5,
                12,
                self.WHITE
            )

            # Start
            fb.text(
                "Start: " + self.format_date(start),
                5,
                22,
                self.WHITE
            )

            # Ende
            fb.text(
                "Ende:  " + self.format_date(end),
                245,
                22,
                self.WHITE
            )

        self.lcd.draw_page(page, draw)

    # --------------------------------------------------
    # Alle Einträge anzeigen
    # --------------------------------------------------

    def show(self, entries):

        gc.collect()

        self.lcd.clear(self.BLACK)

        count = 0

        for entry in entries:

            if count >= 4:
                break

            self.draw_entry(entry, count)

            count += 1

        gc.collect()
