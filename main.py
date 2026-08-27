import caldav
from screen import LCD_3inch5
from task_display import TaskDisplay
import time

LCD = LCD_3inch5()
LCD.bl_ctrl(100)

caldav.connect_wifi()

entries = caldav.get_all_entries()

tasks = caldav.get_current_tasks(entries)

task_tree = caldav.build_task_hierarchy(tasks)

display = TaskDisplay(LCD)

display.show_tasks(task_tree)