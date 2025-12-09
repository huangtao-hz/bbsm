# 项目：   工作平台
# 模块：   版本说明
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2019-01-03 21:08
# 修订：2023-04-17 14:17 从 init 文件获取数据库连接

from orange import arg
from bbsm import db


@arg("-i", "--init", action="store_true", help="初始化数据库")
@arg("-l", "--load", action="store_true", help="导入数据")
@arg("-t", "--tongjia", action="store_true", help="统计所有数据")
@arg("-T", "--tongjib", action="store_true", help="按年统计")
@arg("-q", "--query", metavar="nr", dest="nr", help="查询交易优化记录")
@arg("-Q", "--querysql", metavar="sql", dest="sql", help="执行 sql 语句")
@arg("-e", "--export", action="store_true", help="导出汇总版本说明")
@arg("-p", "--publish", action="store_true", help="生成笔记")
@arg(
    "-r",
    "--report",
    metavar="month",
    dest="rptmonth",
    default="NOSET",
    nargs="?",
    help="生成制定月份的运营报告，默认当月",
)
@arg("jym", nargs="?", help="查询交易优化记录")
def main(**options):
    view = "select rq,xm,count(distinct nr)as sl from bbsm group by rq,xm"
    if options.get("init"):
        db.executefile("bbsm", "bbsm.sql")
        print("创建数据库完成")
    if options.get("tongjia"):
        print(" 投产日期      优化数量")
        db.printf(
            "{}      {:4,d}", f"select rq,sum(sl) from ({view}) group by rq order by rq"
        )
    if options.get("tongjib"):
        print(" 年份    投产次数  优化数量")
        db.printf(
            "{}       {:3d}      {:5,d}",
            'select strftime("%Y",rq)as nf,count(distinct rq),sum(sl) from '
            f"({view}) "
            "group by nf order by nf",
        )

    if options.get("load"):
        from .loadall import load_all

        load_all()
    jym = options.get("jym")
    if jym:
        db.printf(
            "交易码：{}  交易名称：{}",
            "select jym,jymc,lxr from bbsm where jym=? order by rq desc limit 1",
            [jym],
            print_rows=False,
        )
        db.printf(
            "{}    {}\n{}",
            "select rq,lxr,nr from bbsm where jym=? order by rq asc",
            [jym],
        )
    nr = options.get("nr")
    if nr:
        db.printf(
            "{}    {}-{}    {}\n{}",
            'select rq,ifnull(jym,""),jymc,lxr,nr from bbsm where nr like ? order by rq asc',
            [f"%{nr}%"],
        )
    if options.get("export"):
        from bbsm.util.write import export

        export()
    if options.get("publish"):
        from .biji import publish

        print("生成笔记")
        publish()
    sql = options.get("sql")
    if sql:
        db.print(sql)
    rptmonth = options.get("rptmonth")
    if rptmonth != "NOSET":
        from .yybg import baogao

        baogao(rptmonth)


if __name__ == "__main__":
    main()
