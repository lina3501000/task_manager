# --------------------------------------------------
# Imports
# --------------------------------------------------

import caldav
import tasks

from screen import LCD_3inch5
from task_display import TaskDisplay
from calender_screen import CalendarScreen

# WLAN verbinden

caldav.connect_wifi()

entries = caldav.get_all_tasks()

task_tree = caldav.build_task_hierarchy(entries)

for task in task_tree:
    print(task["summary"])
    print(task.get("start", ""))
    print(task.get("due", ""))
    print(task["calendar"])

    for child in task["children"]:
        print("  Unteraufgabe:", child["summary"])

# --------------------------------------------------
# Variablen / Objekte
# --------------------------------------------------

LCD = LCD_3inch5()
LCD.bl_ctrl(100)

screen = CalendarScreen(LCD)


# --------------------------------------------------
# Kalender anzeigen
# --------------------------------------------------

#entries = caldav.get_all_entries()

screen.show(entries)



#tasks = caldav.get_current_tasks(entries)
# --------------------------------------------------
# Beispiele
# --------------------------------------------------

"""
# Aufgaben anzeigen

LCD = LCD_3inch5()
LCD.bl_ctrl(100)

entries = caldav.get_all_entries()
tasks = caldav.get_current_tasks(entries)

display = TaskDisplay(LCD)
display.show_tasks(tasks)

# Aufgabenhierarchie erstellen

task_tree = caldav.build_task_hierarchy(tasks)

caldav.print_task_tree(task_tree)


# Aufgabe abschließen

for task in tasks:

    if task.get("summary") == "Unteraufgabe":

        caldav.complete_task(task)
        break


# Aufgabe erstellen

tasks.create_task(
    summary="TestPut",
    start_date="20260830",
    due_date="20260830",
    calendar="home-2",
    subtasks=[
        "Test Put: Unteraufgabe"
    ]
)
"""