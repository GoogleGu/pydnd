import time
import random


def generate_id():
    """生成 id
    格式 6 位随机整型 + 13 位时间戳
    """

    time_stamp = int(round(time.time() * 1000))
    ints = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    return int(f'{ints}{time_stamp}')
