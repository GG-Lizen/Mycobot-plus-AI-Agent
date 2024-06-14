"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : task_type.py
"""

from enum import Enum
from pydantic import BaseModel
from collections import deque

class TaskTypeDef(BaseModel):
    name: str
    desc: str = ""
    guidance: str = ""

class TaskType(Enum):
    """By identifying specific types of tasks, we can inject human priors (guidance) to help task solving"""

    CONTROL = TaskTypeDef(
        name="control",
        desc="机械臂控制",
    )
    LED = TaskTypeDef(
        name="led",
        desc="led灯控制",
    )
    DETECTION = TaskTypeDef(
        name="detection",
        desc="目标检测，涉及到具体物体时要先其进行目标检测",
    )

    @property
    def type_name(self):
        return self.value.name

    @classmethod
    def get_type(cls, type_name):
        for member in cls:
            if member.type_name == type_name:
                return member
        return None

# 定义任务类
class Task:
    def __init__(self, task_id, dependent_task_ids, instruction, task_type):
        self.task_id = task_id
        self.dependent_task_ids = dependent_task_ids
        self.instruction = instruction
        self.task_type = TaskType.get_type(task_type)
        if self.task_type is None:
            raise ValueError(f"Invalid task type: {task_type}")

    def is_valid_task_type(self):
        return isinstance(self.task_type, TaskType)

# 拓扑排序函数
def topological_sort(tasks):
    # 构建图和入度表
    graph = {task.task_id: [] for task in tasks}
    in_degree = {task.task_id: 0 for task in tasks}

    # 填充图和入度表
    for task in tasks:
        for dep_id in task.dependent_task_ids:
            graph[dep_id].append(task.task_id)
            in_degree[task.task_id] += 1

    # 使用队列进行拓扑排序
    queue = deque([task_id for task_id in in_degree if in_degree[task_id] == 0])
    sorted_tasks = []

    while queue:
        current_task_id = queue.popleft()
        sorted_tasks.append(current_task_id)
        for neighbor in graph[current_task_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_tasks) == len(tasks):
        return sorted_tasks
    else:
        raise Exception("存在循环依赖，无法完成拓扑排序")

# # 按顺序执行任务
# def execute_tasks(tasks):
#     sorted_task_ids = topological_sort(tasks)
#     id_to_task = {task.task_id: task for task in tasks}
#     for task_id in sorted_task_ids:
#         task = id_to_task[task_id]
#         if not task.is_valid_task_type():
#             raise ValueError(f"Invalid task type for task {task_id}: {task.task_type}")
        
#         # 执行任务，根据任务类型进行处理
#         if task.task_type == TaskType.CONTROL:
#             print(f"执行任务 {task.task_id}: {task.instruction}, 类型: CONTROL")
#         elif task.task_type == TaskType.LED:
#             print(f"执行任务 {task.task_id}: {task.instruction}, 类型: LED")
#         elif task.task_type == TaskType.DETECTION:
#             print(f"执行任务 {task.task_id}: {task.instruction}, 类型: DETECTION")
#         else:
#             print(f"未知的任务类型 {task.task_id}: {task.instruction}")


