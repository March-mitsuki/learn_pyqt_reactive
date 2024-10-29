from loguru import logger
import fire
import json
import os
from pathlib import Path
import subprocess

from db.models import init_db, Job, Task, Operation

CWD = Path(os.getcwd())


class Mng:
    def dumpdb(self, path="db.json"):
        logger.info("Dumping Database")

        init_db()
        jobs = Job.select()

        jobs_data = []
        for job in jobs:
            job_data = dict(job.__data__)
            tasks_data = []
            for task in job.tasks:
                task_data = dict(task.__data__)
                task_data["operations"] = [
                    dict(ope.__data__) for ope in task.operations
                ]
                tasks_data.append(task_data)
            job_data["tasks"] = tasks_data
            jobs_data.append(job_data)

        json_data = json.dumps(jobs_data, indent=4)
        with open(path, "w") as f:
            f.write(json_data)

        logger.info(f"Database dumped to {path}")

    def loaddb(self, path="db.json"):
        """
        Insert data from a json file to the database.

        如果修改了数据库模型, 你需要先删除 db.sqlite3 文件

        如果你修改了数据库模型, 又没有设置default值, 那你需要手动修改json文件或者这个函数
        """
        logger.info("Loading Database")

        with open(path, "r") as f:
            data = json.load(f)

        init_db()
        for job_data in data:
            Job.create(**job_data)
            for task_data in job_data["tasks"]:
                Task.create(**task_data)
                for ope_data in task_data["operations"]:
                    Operation.create(**ope_data)

        logger.info(f"Database loaded from {path}")

    def sqliteweb(self, path="db.sqlite3"):
        logger.info("Starting SQLiteWeb")

        cmd_path = CWD / "auto-nikke" / "Scripts" / "sqlite_web.exe"
        subprocess.run([str(cmd_path), path])


if __name__ == "__main__":
    fire.Fire(Mng)
