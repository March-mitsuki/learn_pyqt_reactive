from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    FloatField,
    TextField,
    ForeignKeyField,
    IntegerField,
    BooleanField,
)
import json
from enum import Enum

from .utils import sort_model_by_order

db = SqliteDatabase("db.sqlite3")


def init_db():
    db.connect()
    db.create_tables([Job, Task, Operation])


class JSONField(TextField):
    def python_value(self, value):
        # 从数据库取出时自动解析 JSON 字符串为 Python 对象
        if value is not None:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def db_value(self, value):
        # 存入数据库时自动将 Python 对象转换为 JSON 字符串
        if value is not None:
            return json.dumps(value)
        return value


class OperationType(Enum):
    CLICK_IMG = "click_img"
    CLICK_PERCENT = "click_percent"
    WAIT = "wait"

    def to_choices():
        result = []
        for op_type in OperationType:
            result.append((op_type.value, op_type.value))
        return result

    def to_list():
        return [op_type.value for op_type in OperationType]


class Job(Model):
    name = CharField()
    window_name = CharField()
    task_order = JSONField(default=list())

    class Meta:
        database = db
        table_name = "jobs"

    def get_orded_tasks(self):
        return sort_model_by_order(self.tasks, self.task_order)


class Task(Model):
    """
    One task in a job
    """

    name = CharField()
    ignore_error = BooleanField(default=False)
    skip_this = BooleanField(default=False)
    job = ForeignKeyField(Job, backref="tasks", on_delete="CASCADE")
    operation_order = JSONField(default=list())

    class Meta:
        database = db
        table_name = "tasks"

    def get_orded_operations(self):
        return sort_model_by_order(self.operations, self.operation_order)


class Operation(Model):
    """
    One operation in a task
    """

    name = CharField()
    ignore_error = BooleanField(default=False)
    skip_this = BooleanField(default=False)
    operation_type = CharField(choices=OperationType.to_choices())
    # screen_img 在 click_img 时作为判断是否在当前页面的依据
    # screen_img 在 wait 时作为判断是否已经完成等待的依据
    # screen_img 在 click_percent 时不对判断有任何作用, 只是方便让用户选择一个区域
    screen_img = CharField(null=True)
    click_img = CharField(null=True)
    click_percent_x = FloatField(null=True)
    click_percent_y = FloatField(null=True)
    # click_percent_match_img 为 click_percent 时判断是否在当前页面的依据
    # click_percent_match_img 为 None 时, 代表不需要检查页面
    click_percent_match_img = CharField(null=True)
    click_times = IntegerField(default=1)
    # 当是一个等待任务时, 直接寻找 game_scrren 中是否含有 screen_img
    wait_timeout = IntegerField(null=True)  # 单位秒
    # 当是隐式等待时, 会等完 wait_timeout 秒
    is_implicity_wait = BooleanField(default=False)
    task = ForeignKeyField(Task, backref="operations", on_delete="CASCADE")

    class Meta:
        database = db
        table_name = "operations"
