from caldav_tasks_api import TasksAPI
import os
from dotenv import load_dotenv

load_dotenv()

api = TasksAPI(
    url=os.getenv("base_url"),
    username=os.getenv("username"),
    password=os.getenv("password")
)

api.load_remote_data()

# Aufgabe suchen
test_task = None

for task_list in api.task_lists:
    print(f"List: {task_list.name} ({len(task_list.tasks)} tasks)")

    for task in task_list.tasks:
        if task.uid == "bb6d32e1-4bb7-4f6c-b51d-784a76c99ded":
            test_task = task
            break

    if test_task:
        break

