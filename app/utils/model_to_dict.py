from sqlalchemy.orm import class_mapper, ColumnProperty

def model_to_dict(obj, visited=None):
    """
    序列化 SQLAlchemy 对象，包括其所有关系。跳过: 1.文件类型的字段、2. 用户 relationship。
    :param obj: SQLAlchemy 模型实例
    :param visited: 用于防止循环引用的集合
    :return: 序列化后的字典
    """
    if visited is None:
        visited = set()
    
    if obj in visited:  # 防止循环引用
        return None
    visited.add(obj)

    output = {}
    mapper = class_mapper(obj.__class__)

    # 序列化普通属性
    for attr in mapper.iterate_properties:
        if isinstance(attr, ColumnProperty):
            value = getattr(obj, attr.key)
            # 跳过文件类型
            if (isinstance(value, bytes) == False):
                output[attr.key] = value

    # 序列化 relationship 对象
    for rel in mapper.relationships:
        if (rel.argument  == 'Users'):
            continue
        
        rel_value = getattr(obj, rel.key)

        if rel_value is None:
            output[rel.key] = None
        elif rel.uselist:  # 处理一对多或多对多关系
            sub_model_dicts = [model_to_dict(child, visited) for child in rel_value]
            if (len(sub_model_dicts)):
                output[rel.key] = sub_model_dicts
        else:  # 处理一对一关系
            sub_model_dict = model_to_dict(rel_value, visited)
            if sub_model_dict:
                output[rel.key] = sub_model_dict
    
    visited.remove(obj)
    return output
