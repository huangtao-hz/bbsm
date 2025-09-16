# 项目：版本寿命
# 模块：初始化模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2023-04-14 20:13

from orange import connect, R, datetime

db = connect("bbsm")
db.executefile("bbsm", "bbsm.sql")


def endate(s):
    "格式化日期"
    if not s:
        result = "3000-12-31"
    elif "实际" in s or "发生" in s:
        result = "2100-12-31"
    else:
        try:
            d = datetime(*map(int, (R / r"\d+").findall(s)))
            result = d % "%F %H:%M"
        except Exception:
            result = "3000-12-31"
    return result


db.create_function("replace_str", 4, str.replace)  # 增加自定义函数
db.create_function("endate", 1, endate)  # 增加自定义函数
