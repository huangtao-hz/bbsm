# 项目：   版本验收
# 模块：   数据导入模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-10-12 14:13
from . import Home, Path
from orange import R, first, suppress
from bbsm import db
from typing import Iterable


def read(path: Path) -> Iterable:
    "读取版本验收内容的文件数据"
    sheet = first(Path(path).worksheets)
    data = sheet._cell_values
    merged_cells = sheet.merged_cells
    rq = tuple(map(int, (R / r"\d+").findall(path.pname)))
    rq = f"{rq[0]:04d}-{rq[1]:02d}-{rq[2]:02d}"

    db.execute("delete from ysnr where tcrq=?", [rq])

    def get_mg(row: int, col: int) -> str:
        for r1, r2, c1, c2 in merged_cells:
            if r1 <= row < r2 and c1 <= col < c2:
                return data[r1][c1]
        return ""

    for r, row in enumerate(data[1:], 1):
        # 科技新增了序号栏位
        s = []
        for i in range(1, 11):
            s.append(row[i] if row[i] else get_mg(r, i))
        yield rq, *s


@suppress
@db.tran
def loadfile():
    "导入本期投产版本内容"
    if not Home:
        print("当前工作中无版本验收目录，请确认！")
        return
    path = Home.find("*版本-运营管理部*.xlsx")
    if path:
        db.lcheck("ysnr", path.name, path.mtime)
        db.load("ysnr", 11, data=read(path), clear=False, print_result=True)
