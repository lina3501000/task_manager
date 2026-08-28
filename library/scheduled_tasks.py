import time
import caldav
import gc


# ==================================================
# Einstellungen
# ==================================================

CALENDAR = "home-2"


# ==================================================
# Aufgaben
# ==================================================

TASKS = [

    {
        "name": "Zaehne putzen",
        "type": "daily",
        "children": [
            {"name": "test1"}]
    },


    {
        "name": "Zimmer aufräumen",
        "type": "weekly",
        "weekday": 6, # 0 = Montag, 6 = Sonntag
    },

    {
        "name": "Monatsaufgabe",
        "type": "monthly",
        "day": 1,
    },

    {
        "name": "Alle 3 Tage",
        "type": "interval",
        "days": 3,
        "start": "20260828",
    },

]


# ==================================================
# Datum
# ==================================================

def today_string():

    now = time.localtime()

    return (
        "{:04d}{:02d}{:02d}"
        .format(
            now[0],
            now[1],
            now[2]
        )
    )


# ==================================================
# Tage seit Datum
# ==================================================

def days_between(date1, date2):

    y1 = int(date1[0:4])
    m1 = int(date1[4:6])
    d1 = int(date1[6:8])

    y2 = int(date2[0:4])
    m2 = int(date2[4:6])
    d2 = int(date2[6:8])

    t1 = time.mktime(
        (y1, m1, d1, 0, 0, 0, 0, 0)
    )

    t2 = time.mktime(
        (y2, m2, d2, 0, 0, 0, 0, 0)
    )

    return int((t2 - t1) / 86400)


# ==================================================
# Prüfen, ob Aufgabe heute fällig ist
# ==================================================

def is_due(task):

    now = time.localtime()

    task_type = task.get("type")

    # ------------------------------
    # täglich
    # ------------------------------

    if task_type == "daily":
        return True

    # ------------------------------
    # wöchentlich
    # ------------------------------

    if task_type == "weekly":

        weekday = now[6]

        return weekday == task["weekday"]

    # ------------------------------
    # monatlich
    # ------------------------------

    if task_type == "monthly":

        day = now[2]

        return day == task["day"]

    # ------------------------------
    # alle X Tage
    # ------------------------------

    if task_type == "interval":

        today = today_string()

        difference = days_between(
            task["start"],
            today
        )

        return (
            difference >= 0
            and difference % task["days"] == 0
        )

    return False


# ==================================================
# Aufgabe erstellen
# ==================================================

def create_scheduled_task(task):

    today = today_string()

    # UID ist absichtlich aus Aufgabe + Datum aufgebaut.
    # Dadurch wird dieselbe Tagesaufgabe nicht doppelt erstellt.
    uid = (
        "scheduled-"
        + task["name"].replace(" ", "-")
        + "-"
        + today
    )

    new_task = {
        "uid": uid,
        "summary": task["name"],
        "due": today
    }

    print()
    print("Erstelle geplante Aufgabe:")
    print(task["name"])
    print("Datum:", today)

    return caldav.add_task(
        new_task,
        CALENDAR
    )


# ==================================================
# Tagesprüfung
# ==================================================

def check_scheduled_tasks():

    print()
    print("==============================")
    print("Prüfe geplante Aufgaben")
    print("Datum:", today_string())
    print("==============================")

    created = 0

    for task in TASKS:

        if not is_due(task):
            continue

        print()
        print("Fällig:", task["name"])

        success = create_scheduled_task(task)

        if success:
            created += 1

        gc.collect()

    print()
    print(
        "Geplante Aufgaben erstellt:",
        created
    )

    return created
