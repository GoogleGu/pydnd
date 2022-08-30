import sys



from src.lib.patterns import singleton



@singleton
class HGJLogger:
    """
    在loguru的logger上做了封装，对各个级别的日志打印加入了项目格式的强约束。
    与loguru的logger使用的唯一不同就是在调用logger.info时必须传入两个参数而不是一个，第一个参数为本条日志的功能
    主题，第二个为日志内容，二者会被合并成'【日志主题】日志内容'的形式作为传给loguru的logger的日志记录内容。

    该封装只封装5个级别的日志打印方法，所有其他的loguru功能都在HGJLogger.loguru_logger上调用。 loguru支持自定
    义日志级别、日志多种方式落盘、自定义日志格式、和notifiers库搭配使用在报错时发送通知邮件等所有日志相关功能，相关文档如下

    - [pypi上loguru页面](https://pypi.org/project/loguru/)
    - [github loguru仓库](https://github.com/Delgan/loguru)
    - [loguru官方文档](https://loguru.readthedocs.io/en/stable/)


    ## HGJLogger的使用代码示例
    ```python
    from src.middleware.log import logger

    # 普通日志打印
    logger.debug('示例', '这是一条debug日志')
    logger.info('示例', '这是一条info日志')
    logger.error('示例','这是一条error日志')
    logger.critical('示例','这是一条critical日志')

    # 日志打印落盘
    logger.loguru_logger.add("file_1.log", rotation="500 MB")    # logger的所有日志存到file_1.log，并在到500MB时创建新的文件来落盘日志
    logger.loguru_logger.add("file_2.log", rotation="12:00")     # 每天12点创建新的日志文件
    logger.loguru_logger.add("file_3.log", rotation="1 week")    # 每周创建新的日志文件
    logger.loguru_logger.add("file_X.log", retention="10 days")  # 每10天清理日志文件
    logger.loguru_logger.add("out.log", backtrace=True, diagnose=True) # 落盘的日志中会同时打印错误堆栈信息和异常发生时各变量的值
    logger.loguru_logger.add("special.log", filter=lambda record: record["level"].name == "ERROR") # 只打印ERROR级别的日志到special中

    # 使用函数级装饰器收集函数内所有错误日志
    @logger.loguru_logger.catch
    def my_function(x, y, z):
        return 1 / (x + y + z)
    """
    def __init__(self) -> None:
        from loguru import logger
        logger.remove()
        logger.add(sys.stderr, backtrace=True, diagnose=False)
        self.loguru_logger = logger.opt(depth=1)

    def debug(self, message, *args, **kwargs):
        content = f'{message}'
        self.loguru_logger.debug(content, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        content = f'{message}'
        self.loguru_logger.info(content, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        content = f'{message}'
        self.loguru_logger.warning(content, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        content = f'{message}'
        self.loguru_logger.error(content, *args, **kwargs)

    def exception(self, message, *args, **kwargs):
        content = f'{message}'
        self.loguru_logger.exception(content, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        content = f'{message}'
        self.loguru_logger.opt(exception=True).critical(content, *args, **kwargs)


logger = HGJLogger()