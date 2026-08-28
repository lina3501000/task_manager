import time
import caldav
import gc
import tasks

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
# Datum + X Tage
# ==================================================

def add_days(date_string, days):

    year = int(date_string[0:4])
    month = int(date_string[4:6])
    day = int(date_string[6:8])

    timestamp = time.mktime(
        (
            year,
            month,
            day,
            0,
            0,
            0,
            0,
            0
        )
    )

    timestamp += days * 86400

    result = time.localtime(timestamp)

    return (
        "{:04d}{:02d}{:02d}"
        .format(
            result[0],
            result[1],
            result[2]
        )
    )


# ==================================================
# Tage zwischen zwei Daten
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

    return int(
        (t2 - t1) / 86400
    )


# ==================================================
# Prüfen, ob Aufgabe HEUTE ERSTELLT werden soll
# ==================================================

def is_due_to_create(task):

    now = time.localtime()

    task_type = task.get("type")


    # --------------------------------------------------
    # täglich
    # --------------------------------------------------

    if task_type == "daily":

        return True


    # --------------------------------------------------
    # wöchentlich
    # --------------------------------------------------

    if task_type == "weekly":

        weekday = now[6]

        if "weekdays" in task:

            return (
                weekday
                in task["weekdays"]
            )

        return (
            weekday
            == task["weekday"]
        )


    # --------------------------------------------------
    # monatlich
    # --------------------------------------------------

    if task_type == "monthly":

        return (
            now[2]
            == task["day"]
        )


    # --------------------------------------------------
    # jährlich
    # --------------------------------------------------

    if task_type == "yearly":

        return (
            now[1]
            == task["month"]
            and
            now[2]
            == task["day"]
        )


    # --------------------------------------------------
    # Montag bis Freitag
    # --------------------------------------------------

    if task_type == "weekdays":

        return now[6] < 5


    # --------------------------------------------------
    # Wochenende
    # --------------------------------------------------

    if task_type == "weekend":

        return now[6] >= 5


    # --------------------------------------------------
    # Alle X Tage
    # --------------------------------------------------

    if task_type == "interval":

        today = today_string()

        difference = days_between(
            task["start"],
            today
        )

        return (
            difference >= 0
            and
            difference
            % task["days"]
            == 0
        )


    # --------------------------------------------------
    # Bestimmte Daten
    # --------------------------------------------------

    if task_type == "specific_days":

        return (
            today_string()
            in task["dates"]
        )


    return False


# ==================================================
# UID
# ==================================================

def make_uid(
    name,
    creation_date,
    suffix=""
):

    uid = (
        "scheduled-"
        + name.replace(" ", "-")
        + "-"
        + creation_date
    )

    if suffix:

        uid += (
            "-"
            + suffix
        )

    return uid


# ==================================================
# Unteraufgaben
# ==================================================

def create_children(
    children,
    parent_uid,
    calendar,
    creation_date,
    due_date
):

    for number, child in enumerate(children):

        child_name = child["name"]

        child_uid = make_uid(
            child_name,
            creation_date,
            str(number)
        )

        child_task = {
            "uid": child_uid,

            "summary": child_name,

            "due": due_date,

            "related_to": parent_uid
        }

        print()
        print(
            "Erstelle Unteraufgabe:",
            child_name
        )

        success = caldav.add_task(
            child_task,
            calendar
        )

        if not success:

            print(
                "Fehler bei Unteraufgabe"
            )

        gc.collect()


# ==================================================
# Geplante Aufgabe erstellen
# ==================================================

def create_scheduled_task(task):

    creation_date = today_string()

    name = task["name"]

    calendar = task["calendar"]


    # --------------------------------------------------
    # Fälligkeitsdatum berechnen
    # --------------------------------------------------

    due_after = task.get(
        "due_after",
        0
    )

    due_date = add_days(
        creation_date,
        due_after
    )


    # --------------------------------------------------
    # UID
    # --------------------------------------------------

    uid = make_uid(
        name,
        creation_date
    )


    # --------------------------------------------------
    # Aufgabe
    # --------------------------------------------------

    new_task = {

        "uid": uid,

        "summary": name,

        "due": due_date
    }


    print()
    print("==============================")
    print("Erstelle Aufgabe")
    print("Name:", name)
    print("Kalender:", calendar)
    print("Erstellt:", creation_date)
    print("Fällig:", due_date)
    print("==============================")


    # --------------------------------------------------
    # Hauptaufgabe
    # --------------------------------------------------

    success = caldav.add_task(
        new_task,
        calendar
    )


    if not success:

        print(
            "Hauptaufgabe konnte nicht erstellt werden"
        )

        return False


    # --------------------------------------------------
    # Unteraufgaben
    # --------------------------------------------------

    children = task.get(
        "children",
        []
    )


    if children:

        print(
            "Unteraufgaben:",
            len(children)
        )

        create_children(
            children,
            uid,
            calendar,
            creation_date,
            due_date
        )


    return True


# ==================================================
# Tagesprüfung
# ==================================================

def check_scheduled_tasks():

    print()
    print("==============================")
    print("Prüfe geplante Aufgaben")
    print(
        "Heute:",
        today_string()
    )
    print("==============================")


    created = 0


    for task in tasks.TASKS:

        print()
        print(
            "Prüfe:",
            task["name"]
        )


        # --------------------------------------------------
        # Heute nicht erstellen
        # --------------------------------------------------

        if not is_due_to_create(task):

            print(
                "Heute keine Erstellung"
            )

            continue


        # --------------------------------------------------
        # Heute erstellen
        # --------------------------------------------------

        print(
            "Heute wird Aufgabe erstellt"
        )


        success = create_scheduled_task(
            task
        )


        if success:

            created += 1


        gc.collect()


    print()
    print("==============================")
    print(
        "Aufgaben erstellt:",
        created
    )
    print("==============================")


    return created

