import uuid
import time
import gc

import caldav


def _date(value):
    """YYYYMMDD aus Datum holen."""
    if isinstance(value, str):
        return value[:8]
    return ""


def _create_task_data(summary, start_date, due_date, parent=None):
    """Erstellt ein Task-Dictionary für caldav.add_task()."""

    task = {
        "uid": str(uuid.uuid4()),
        "summary": summary,
        "start": _date(start_date),
        "due": _date(due_date),
    }

    if parent:
        task["related_to"] = parent

    return task


def create_task(
    summary,
    start_date,
    due_date,
    calendar,
    subtasks=None
):
    """
    Erstellt eine Aufgabe und optional deren Unteraufgaben.

    Gibt die UID der Hauptaufgabe zurück.
    """

    if subtasks is None:
        subtasks = []

    print()
    print("Erstelle Aufgabe:", summary)

    # Hauptaufgabe
    parent = _create_task_data(
        summary,
        start_date,
        due_date
    )

    if not caldav.add_task(parent, calendar):
        print("Hauptaufgabe konnte nicht erstellt werden")
        return None

    parent_uid = parent["uid"]

    print("Hauptaufgabe erstellt")
    print("UID:", parent_uid)

    # Unteraufgaben
    for subtask in subtasks:

        print()
        print("Erstelle Unteraufgabe:", subtask)

        child = _create_task_data(
            subtask,
            start_date,
            due_date,
            parent=parent_uid
        )

        if caldav.add_task(child, calendar):
            print("Unteraufgabe erstellt")
        else:
            print("Unteraufgabe konnte nicht erstellt werden")

        gc.collect()

    return parent_uid
