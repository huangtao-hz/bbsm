# 项目：   版本说明
# 模块：   写入文件模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2022-04-20 21:38

from orange import Path, wlen
from math import ceil
from bbsm import db
from bbsm.util.rymd import get_zg


def write_cell(book, start, end, data, shenpi):
    """
    填写单元格内容：优化原因	验证机构	要求完成时间	验证要求	联系人  审批人
    """
    for col, i, fmt in zip(
        "FGHIJ", range(5), ["normal1", "normal1", "normal1", "normal1", "normal2"]
    ):
        book[f"{col}{start}:{col}{end}"] = data[i], fmt  # 填写其他内容
    if shenpi:
        a = set()
        if not data[-1]:
            return
        spr = get_zg(data[-1])
        if not spr:
            print("Error:", data[-1], "无对应审批人")
        a.add(spr)
        book[f"K{start}:K{end}"] = "、".join(a), "normal2"


def write_nr(book, rq, xm, row, shenpi):
    """
    填写内容
    """
    sql = (
        "select nr,count(nr),min(endate(wcsj))as sj,min(jym)as jy from bbsm "
        "where xm=? and rq=? group by nr order by sj,rowid"
    )
    for nr, count, _, __ in db.fetch(sql, [xm, rq]):
        # print(_)
        book[f"E{row}:E{row + count - 1}"] = nr, "normal1"  # 填写内容
        height = max(
            (sum(ceil(wlen(x) / 72) for x in nr.splitlines()) * 11 + 10) / count, 20
        )  # 计算单元格高度
        if count == 1:  # 单行处理逻辑
            sql = (
                "select jym,jymc,yhyy,yzjg,wcsj,yzyq,lxr from bbsm "
                "where xm=? and nr=? and rq=? order by endate(wcsj),jym"
            )
            d = db.fetchone(sql, [xm, nr, rq])
            book[f"C{row}"] = d[:2], "normal1"  # 填写交易码、交易名称
            write_cell(book, row, row, d[2:], shenpi)  # 填写其他内容
            book.worksheet.set_row(row - 1, height)  # 设置高度
            row = row + 1
        else:  # 多行处理逻辑
            dd = []
            start = row
            sql = (
                "select jym,jymc,yhyy,yzjg,wcsj,yzyq,lxr from bbsm "
                "where xm=? and nr=? and rq=? order by endate(wcsj),jym"
            )
            for d in db.fetch(sql, [xm, nr, rq]):
                book[f"C{row}"] = d[:2], "normal1"  # 填写交易码、交易名称
                book.worksheet.set_row(row - 1, height)  # 设置高度
                if dd != d[2:]:
                    if dd:
                        write_cell(book, start, row - 1, dd, shenpi)  # 填写其他内容
                    start = row
                    dd = d[2:]
                row = row + 1
            write_cell(book, start, row - 1, dd, shenpi)  # 填写其他内容


def write_xm(book, rq: str, shenpi=False):
    """
    填写项目
    """
    row = 2
    sql = (
        "select min(rowid)as xh,xm,count(nr)from bbsm "
        "where rq=? group by xm having count(nr)>0 order by xh"
    )
    end = 2
    for bh, (_, xm, count) in enumerate(db.fetch(sql, [rq]), 1):
        end = row + count
        book[f"A{row}:A{end - 1}"] = bh, "normal2"  # 填写项目序号
        book[f"B{row}:B{end - 1}"] = xm, "normal2"  # 填写项目名称
        write_nr(book, rq, xm, row, shenpi)  # 填写内容
        row = end
    if shenpi:
        book.set_border(f"A1:K{end - 1}")  # 设置表格边框
    else:
        book.set_border(f"A1:J{end - 1}")  # 设置表格边框


formats = {
    "header": {"font_name": "黑体", "font_size": 9, "align": "center"},
    "normal1": {
        "font_name": "宋体",
        "font_size": 9,
        "valign": "vcenter",
        "text_wrap": True,
    },
    "normal2": {
        "font_name": "宋体",
        "font_size": 9,
        "valign": "vcenter",
        "align": "center",
        "text_wrap": True,
    },
}

widths = {
    "A:A": 5,
    "B:B": 21,
    "C:C": 6,
    "D:D": 30,
    "E:E": 60,
    "F:G": 15,
    "H:I": 20,
    "J:J": 10,
}

title = "序号,系统或项目,交易码,交易名称,优化内容,优化原因,验证机构,要求完成时间,验证要求,联系人".split(
    ","
)


def write(path, rq: str, shenpi=False):
    """按新的格式重新填写 Excel 表"""
    # 先备份原文件

    # 填写表头
    # path = path.with_name(path.pname+'_test.xlsx')
    with path.write_xlsx(force=True) as book:
        book.add_formats(formats)  # 添加自定义格式
        book.worksheet = rq  # 设置工作表名称
        book.set_widths(widths)  # 设置宽度
        if shenpi:
            title.append("审批人")
        book["A1"] = title, "header"  # 设置表头
        write_xm(book, rq, shenpi)  # 填写项目
        print("更新格式完成")


def write_year(path: Path, year: str):
    """按年导出 Excel 表"""
    with path.write_xlsx(force=True) as book:
        book.add_formats(formats)  # 添加自定义格式
        for (rq,) in db.fetch(
            f'select distinct rq from bbsm where rq like "{year}%" order by rq desc'
        ):
            book.worksheet = str(rq)  # 设置工作表名称
            book.set_widths(widths)  # 设置宽度
            book["A1"] = title, "header"  # 设置表头
            write_xm(book, rq)  # 填写项目
        print(f"版本说明-{year}", "导出完成")


def export():
    Home = Path("~/Documents/版本说明汇总")
    Home.ensure()
    flag = True
    for (year,) in db.fetch(
        "select distinct substr(rq,1,4)as year from bbsm order by year desc"
    ):
        path = Home / f"版本说明-{year}.xlsx"
        if flag:
            write_year(path, year)
            flag = False
        elif path:
            print(path.pname, "跳过")
        else:
            write_year(path, year)
