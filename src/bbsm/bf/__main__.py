# 项目：   版本说明
# 模块：   格式化版本说明
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2022-04-20 22:01
# 修订：2023-04-20 10:53 增加 publish 参数，选择时不输出审批人，未选择时，输出审批人

import shutil

from orange import Path, arg, command, extract


@command(description="版本说明格式化程序", allow_empty=True)
@arg("-p", "--publish", action="store_true", help="发布版本说明")
@arg("-d", "--delete", nargs="?", metavar="tcrq", help="删除指定日期的版本")
def main(**options):
    Home = Path("~/Documents/当前工作")
    from bbsm import db
    from bbsm.util.load import load
    from bbsm.util.rymd import load_rymd
    from bbsm.util.write import write

    from .check import check

    load_rymd()
    path = Home.find("附件*版本说明????????.xls*")  # 查找版本说明文件
    dtcrq = options.get("delete")
    if dtcrq:
        print("删除指定日期的投产版本内容", dtcrq)
        last_tcrq = db.fetchvalue("select max(rq) from bbsm")
        if dtcrq != last_tcrq:
            raise Exception(f"{dtcrq} 不是最近一期内容，不能删除！")
        with db:
            r = db.execute("delete from bbsm where rq=?", [dtcrq])
            print(f"共删除 {r.rowcount} 条记录")
        return
    # if options.get('update'):
    # from .yzap import update_anpai, write_anpai, get_yzfh
    # update_anpai()
    # get_yzfh(None)
    # write_anpai()
    if path:
        print("当前文件：", path.name)
        rq = extract(path.name, r"\d{8}")
        rq = f"{rq[:4]}-{rq[4:6]}-{rq[6:]}"
        shutil.copy(path, path.with_name(f"{path.pname}_bak{path.suffix}"))
        load(path)
        check(rq, publish=bool(options.get("publish")))
        write(path, rq, shenpi=not options.get("publish"))
        tzwj = path.parent / f"关于下发系统版本说明（{rq.replace('-', '')}）的通知.docx"
        if not tzwj:
            from .tctz import tctz

            print("生成通知文件")
            tctz(tzwj, rq)

        # path=path.with_name(path.pname+'（审批版）.xlsx')
        # write(path, rq, shenpi=True)
    else:
        print("未发现版本说明文件")


if __name__ == "__main__":
    main()
