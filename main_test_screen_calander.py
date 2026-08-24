import caldav
from screen import LCD_3inch5
from task_display import TaskDisplay


LCD = LCD_3inch5()
LCD.bl_ctrl(100)


tasks = caldav.get_all_tasks()


display = TaskDisplay(LCD)
display.show_tasks(tasks)