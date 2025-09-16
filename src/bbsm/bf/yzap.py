# 项目：   版本说明
# 模块：   投产安排
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-04-28 10:37

from bbsm import db
from orange import date, Path, suppress
from orange.xlsx import Header
from typing import Iterable

path = Path("E:/Personal/工作/参数备份/验证安排/验证安排分行.xlsx")


@suppress
@db.tran
def update_anpai():
    "更新验证分行安排"

    db.lcheck("yzanpai", path, path.mtime, None)
    print("导入验证安排分行")

    def read() -> Iterable:
        for row in path.read_sheet(start_row=1):
            for fh in row[1].split("、"):
                print(fh, date(row[0]), row[2])
                yield fh, date(row[0]), row[2]

    db.load("yzanpai", 3, read(), clear=True, method="replace", print_result=True)


@suppress
@db.tran
def write_anpai():
    sql = 'select rq,group_concat(fh,"、"),nr from yzanpai group by rq order by rq'
    db.export(
        path, sql, columns=[Header("日期", 10), Header("分行", 40), Header("备注", 25)]
    )
    db.lcheck("yzanpai", path, path.mtime, None)


q_sql = """
select a.mc,b.sl,b.kbrq,c.zjrq
from branch a
left join (select hzjgm,count(jgm)as sl,min(kbrq)as kbrq from ggjgm where jglx="12" group by hzjgm) b on a.jgm=b.hzjgm
left join (select fh,max(rq)as zjrq from yzanpai group by fh) c on a.mc=c.fh
where a.mc<>'义乌分行'
and b.sl>=10
order by zjrq,sl asc,kbrq asc
limit 5
"""

m_sql = """
select a.mc,b.sl,b.kbrq,c.zjrq
from branch a
left join (select hzjgm,count(jgm)as sl,min(kbrq)as kbrq from ggjgm where jglx="12" group by hzjgm) b on a.jgm=b.hzjgm
left join (select fh,max(rq)as zjrq from yzanpai group by fh) c on a.mc=c.fh
where a.mc<>'义乌分行'
and b.sl>=5
order by zjrq,b.sl desc,kbrq desc
limit 5
"""
w_sql = """
select a.mc,b.sl,b.kbrq,c.zjrq
from branch a
left join (select hzjgm,count(jgm)as sl,min(kbrq)as kbrq from ggjgm where jglx="12" group by hzjgm) b on a.jgm=b.hzjgm
left join (select fh,max(rq)as zjrq from yzanpai group by fh) c on a.mc=c.fh
where a.mc<>'义乌分行'
and b.sl<5
order by zjrq
limit 5
"""


def get_yzfh(rq):
    db.attach("params", "pa")
    try:
        s = input("请输入验证内容（Q-季度版本，M-月度版本，W-临时验证）:")
        s = s.upper()
        if s == "Q":
            db.print(q_sql)
        elif s == "M":
            db.print(m_sql)
        else:
            db.print(w_sql)

    finally:
        db.detach("pa")
