import caldav

caldav.connect_wifi()

entries = caldav.get_all_entries()

tasks = caldav.get_current_tasks(entries)

task_tree = caldav.build_task_hierarchy(tasks)

print()
caldav.print_task_tree(task_tree)
for task in tasks:

    if task.get("summary") == "Unteraufgabe":

        caldav.complete_task(task)
        break