# 项目：   版本说明
# 模块：   检查交易参数模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2022-04-20 21:38
# 修订：2022-05-11 15:27 修正投产日期小于当前日期系统提醒的 bug

import uuid

from orange import R, now

from bbsm import db

"""
@db.tran
def update_leibie(tcrq):
    '''
修正优化原因，将各式各样的，如“交易优化”“功能优化”“优化功能”统一为“功能优化”
'''
    print('修正优化原因')
    for k, v in LeiBie.items():
        if k != v:
            r1 = db.execute(  # 修改优化原因
                'update bbsm set yhyy=? where yhyy=? and rq=?', [v, k, tcrq])
            r2 = db.execute(  # 修改优化内容
                'update bbsm set nr=replace_str(nr,?,?,1)where nr like ? and rq=?', [k, v, k+'%', tcrq])
            print(k, '->', v, r1.rowcount, r2.rowcount)
"""


@db.tran
def update_yzsj(tcrq, publish=False):
    """
    更新验证时间，对于已安排验证时间的，校验安排的是否合理。对于不合理的安排进行提示。
    对于未安排验证的，设置默认的验证时间。一般个人交易安排在次日7:30前，公司业务安排在次日12:00前。
    """
    print("设置验证时间")
    yzsj = db.fetchvalue('select date(?,"1 day")', [tcrq])
    if isinstance(yzsj, str):
        yzsj = "{}年{}月{}日".format(*map(int, yzsj.split("-")))
    else:
        yzsj = ""

    # 检查安排时间错误
    obj = db.fetch(
        "select jym,jymc,yzsj from bbsm where rq=? and date(endate(yzsj))<=rq ", [tcrq]
    )
    if obj:
        print("存在验证时间错误数据：")
        for r in obj:
            print(*r)

    r = db.execute(
        'update bbsm set wcsj=? where rq=? and ifnull(wcsj,"")="" and jym in '
        '(select jym from jymb where jyz in("TG001P","TG003P","TG999P","TG501P","TG908F","TG902F") )',
        [
            yzsj + " 7:30前",
            tcrq,
        ],
    )
    print("个人业务：", r.rowcount)
    r = db.execute(
        'update bbsm set wcsj=? where rq=? and ifnull(wcsj,"")="" and jym in '
        '(select jym from jymb where jyz in("TG002P","TG101P","TG502P","TG102P") )',
        [
            yzsj + " 12:00前",
            tcrq,
        ],
    )
    print("单位业务：", r.rowcount)
    if publish:
        r = db.execute(
            'update bbsm set yzyq="验证相关功能正常" where rq=? and ifnull(yzyq,"")="" ',
            [tcrq],
        )
        print("更新验证要求：", r.rowcount)


def modify(jym: str, jymc: str, tcrq: str):
    obj = db.fetchone("select * from jymb where jym =?", [jym])
    obj = [
        uuid.uuid1().hex,
        jymc,
        *obj[1:],
        None,
        None,
        None,
        "变更",
        now() % "%F",
        max(tcrq, now() % "%F"),
    ]
    with db:
        db.load("jycsb", fields=32, data=[obj], method="replace", clear=False)
        print("更新投产参数表完成！")


def docheck(tcrq):
    sql = 'select distinct jym,jymc,lxr from bbsm where jym is not null and jym<>"F4" and rq=?'
    Pattern = R / r"\d{4}"
    for jym, jymc, lxr in filter(lambda row: Pattern == row[0], db.fetch(sql, [tcrq])):
        query_sql = "select jym,jymc,jymc=? from jym where jym=?"
        obj = db.fetchone(query_sql, [jymc, jym])
        if obj:
            if not obj[2] and not db.fetchone(
                'select jym from jycsb where jym=? and bz="变更" and tcrq>=?',
                [jym, tcrq],
            ):
                print(
                    f"交易名不符：交易码：{jym}，参数名称：{obj[1]}，版本名称：{jymc}，联系人：{lxr}"
                )
                p = input("M:修改生产参数，U:更新版本说明，其他键忽略")
                p = p.lower()
                if p == "u":
                    with db:
                        db.execute(
                            "update bbsm set jymc=? where jym=? and lxr=? and rq=?",
                            [obj[1], jym, lxr, tcrq],
                        )
                        print("更新版本说明完成！")
                elif p == "m":
                    modify(jym, jymc, tcrq)
        else:
            one = db.fetchone(
                'select [id],jym,jymc,tcrq from jycsb where jym=? and ifnull(bz,"") <>"变更" ',
                [jym],
            )
            if not one:
                print(f"交易码不存在：交易码：{jym}-{jymc}，联系人:{lxr}")
            elif not one[-1] or one[-1] > tcrq:
                print(
                    f"投产日期不正确：交易：{jym}-{jymc}，联系人：{lxr}，原投产日期：{one[-1]}"
                )
                p = input("请确认，Y 或 N？")
                if p.lower() == "y":
                    with db:
                        db.execute(
                            "update jycsb set tcrq=? where [id]=?", [tcrq, one[0]]
                        )
                        print("更新投产日期完成！")


def check(tcrq, publish=False):
    db.attach("params", "pa")
    try:
        docheck(tcrq)
        # update_leibie(tcrq)  # 更新优化云因
        update_yzsj(tcrq, publish)  # 设置投产时间
    finally:
        db.detach("pa")
