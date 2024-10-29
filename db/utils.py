def sort_model_by_order(model_select, order: list[int]):
    if len(order) <= 0:
        return list(model_select)
    data = list(model_select)
    data_dict = {item.id: item for item in data}
    result = [data_dict[i] for i in order if i in data_dict]

    # 如果 order 长度不等于 data, 把剩下的放到最后
    order_set = set(order)
    result.extend(item for item in data if item.id not in order_set)

    return result

    # [data_dict[i] for i in order if i in data_dict] 等价于:
    # result = []
    # for i in order:
    #     if i in data_dict:
    #         result.append(data_dict[i])
    # return result


def find_first(data: list, lambda_func):
    for item in data:
        if lambda_func(item):
            return item
    return None
