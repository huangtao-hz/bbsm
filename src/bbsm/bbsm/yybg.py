# 项目：   版本说明
# 模块：   运营管理报告（版本说明）
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-04-17 14:21

from collections import defaultdict
from typing import Optional

from bbsm import db


def baogao(rptmonth: Optional[str] = None):
    if not rptmonth:
        yf = db.fetchvalue("select max(rq) from bbsm")[:7]  # 获取当前月份
        assert yf is not None and isinstance(yf, str)
    else:
        yf = rptmonth
    print("月份：", yf)
    cs = db.fetchvalue(
        "select count(distinct rq) from bbsm where rq like ?", [f"{yf}%"]
    )
    if cs:
        counter = defaultdict(lambda: 0)
        zs = 0
        for yy, sl in db.fetch(
            "select yhyy,count(distinct nr) from bbsm where rq like ? group by yhyy",
            [f"{yf}%"],
        ):
            if not yy:
                continue
            if "修复" in yy:
                counter["xf"] += sl
                zs += sl
            elif "新增" in yy:
                counter["xz"] += sl
                zs += sl
            else:
                counter["yh"] += sl
                zs += sl

        y = int(yf.split("-")[-1])
        s = f"{y}月共实施{cs}次系统优化版本，投产{zs}项功能，其中新增功能{counter['xz']}项，优化功能{counter['yh']}项，修复问题{counter['xf']}项。"
        print(s)
    else:
        print("该月份无投产内容")
