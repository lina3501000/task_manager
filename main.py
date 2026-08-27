import caldav
from screen import LCD_3inch5
from task_display import TaskDisplay
import time

LCD = LCD_3inch5()
LCD.bl_ctrl(100)

caldav.connect_wifi()

"""task = {
    "uid": "test124",
    "summary": "NeueAufgabe",
    "due": "20260830",
    "subtasks": ["test"]
}

caldav.add_task(task, "home-2")"""

entries = caldav.get_all_entries()

tasks = caldav.get_current_tasks(entries)

task_tree = caldav.build_task_hierarchy(tasks)

display = TaskDisplay(LCD)

display.show_tasks(task_tree)