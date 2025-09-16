# 项目：   版本说明
# 模块：   版本验收-报告版本说明提交情况
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-11-20 08:46


from bbsm import db


def report():
    "报告未提交版本说明的人员清单"
    rq = db.fetchvalue("select max(rq)from bbsm")
    print("当前日期：", rq)
    renyuan = db.fetchvalue(
        "select group_concat(distinct lxr)from bbsm where rq=?", [rq]
    )
    if isinstance(renyuan, str):
        renyuan = ",".join(map(lambda x: f'"{x}"', renyuan.split(",")))

    print("未提交版本说明人员：")
    db.print(
        f"select distinct tcrq, ysry from ysnr where ysry not in ({renyuan}) and tcrq=?",
        [rq],
    )
