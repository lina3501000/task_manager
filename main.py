import caldav
from screen import LCD_3inch5
from task_display import TaskDisplay
import time
import scheduled_tasks

LCD = LCD_3inch5()
LCD.bl_ctrl(100)

caldav.connect_wifi()

scheduled_tasks.check_scheduled_tasks()

tasks = caldav.get_all_tasks()

task_tree = caldav.build_task_hierarchy(tasks)

display = TaskDisplay(LCD)
display.show_tasks(task_tree)