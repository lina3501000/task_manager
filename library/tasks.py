# ==================================================
# Aufgaben-Konfiguration
# ==================================================
#
# Diese Datei enthält nur die Aufgaben-Konfiguration.
#
# Unterstützte Typen:
#
#   daily
#   weekly
#   monthly
#   yearly
#   weekdays
#   weekend
#   interval
#   specific_days
#
# "due_after" gibt an, wie viele Tage nach der
# Erstellung die Aufgabe fällig wird.
#
# Beispiel:
#
#   due_after: 0
#       → heute erstellen, heute fällig
#
#   due_after: 2
#       → heute erstellen, in 2 Tagen fällig
#
# Unteraufgaben können mit "children" angegeben werden.
#
# ==================================================


TASKS = [

    # --------------------------------------------------
    # TÄGLICH
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "daily",

        "due_after": 0,
    },


    # --------------------------------------------------
    # WÖCHENTLICH
    # --------------------------------------------------
    #
    # weekday:
    #
    #   0 = Montag
    #   1 = Dienstag
    #   2 = Mittwoch
    #   3 = Donnerstag
    #   4 = Freitag
    #   5 = Samstag
    #   6 = Sonntag
    #
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "weekly",

        "weekday": 4,

        # Freitag erstellen
        # Sonntag fällig
        "due_after": 2,
    },


    # --------------------------------------------------
    # MONATLICH
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "monthly",

        # Am 1. des Monats erstellen
        "day": 1,

        "due_after": 5,
    },


    # --------------------------------------------------
    # JÄHRLICH
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "yearly",

        # Monat: 12 = Dezember
        "month": 12,

        # Tag
        "day": 24,

        "due_after": 0,
    },


    # --------------------------------------------------
    # MONTAG BIS FREITAG
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "weekdays",

        "due_after": 0,
    },


    # --------------------------------------------------
    # WOCHENENDE
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "weekend",

        "due_after": 1,
    },


    # --------------------------------------------------
    # ALLE X TAGE
    # --------------------------------------------------
    #
    # Beispiel:
    # alle 3 Tage ab dem 28.08.2026
    #
    # 28.08.
    # 31.08.
    # 03.09.
    # 06.09.
    # ...
    #
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "interval",

        "days": 3,

        "start": "20260828",

        "due_after": 2,
    },


    # --------------------------------------------------
    # ALLE X WOCHEN
    # --------------------------------------------------
    #
    # Eine Woche = 7 Tage
    #
    # Alle 2 Wochen:
    # days = 14
    #
    # Alle 3 Wochen:
    # days = 21
    #
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "interval",

        "days": 21,

        "start": "20260828",

        "due_after": 2,
    },


    # --------------------------------------------------
    # BESTIMMTE DATEN
    # --------------------------------------------------
    #
    # Die Aufgabe wird nur an den angegebenen
    # Tagen erstellt.
    #
    # Format: YYYYMMDD
    #
    # --------------------------------------------------

    {
        "name": "Aufgabe",
        "calendar": "KALENDER",

        "type": "specific_days",

        "dates": [
            "20261224",
            "20261231",
            "20270101",
        ],

        "due_after": 0,
    },


    # --------------------------------------------------
    # AUFGABE MIT UNTERAUFGABEN
    # --------------------------------------------------
    #
    # Unteraufgaben werden automatisch als VTODOs
    # erstellt und über RELATED-TO mit der
    # Hauptaufgabe verknüpft.
    #
    # --------------------------------------------------

    {
        "name": "Hauptaufgabe",
        "calendar": "KALENDER",

        "type": "weekly",

        "weekday": 4,

        "due_after": 2,

        "children": [
            {
                "name": "Unteraufgabe 1"
            },
            {
                "name": "Unteraufgabe 2"
            },
            {
                "name": "Unteraufgabe 3"
            }
        ]
    },

]
