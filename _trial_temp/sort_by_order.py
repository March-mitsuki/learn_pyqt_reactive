def sort_model_by_order(data: list, order: list[int]):
    data_dict = {item.id: item for item in data}  # 构建字典
    result = []  # 初始化结果列表
    for i in order:  # 遍历 order 列表
        if i in data_dict:  # 检查 i 是否在 data_dict 中
            result.append(data_dict[i])  # 如果存在，添加对应的对象到结果列表
    return result  # 返回结果列表


# 测试代码保持不变
ids = [1, 2, 3, 4, 5]


class Model:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self) -> str:
        return f"Model({self.id}, {self.name})"


data = [
    Model(1, "a"),
]

print(sort_model_by_order(data, ids))
