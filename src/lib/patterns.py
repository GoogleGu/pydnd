import functools


def singleton(cls):
    """
    将被装饰的类变为单例
    使用例子：
    @singleton
    class DemoClass():
        pass
    """
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance