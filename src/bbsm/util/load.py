# 项目：   版本说明
# 模块：   导入数据模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2022-04-20 21:38
# 修订：2023-04-20 11:01 对导入的数据，删除前后不可见字符

from orange import Path, extract, first
from bbsm import db, endate
from typing import Iterable


def read(path: Path) -> Iterable:
    sheet = first(Path(path).worksheets)
    data = sheet._cell_values
    rq = extract(sheet.name, r"\d{4}-?\d{2}-?\d{2}").replace("-", "")
    rq2 = extract(path.pname, r"\d{8}")
    if rq != rq2:
        raise Exception(f"文件名中日期 {rq2} 与工作表中日期 {rq} 不一致")
    merged_cells = sheet.merged_cells
    rq = f"{rq[:4]}-{rq[4:6]}-{rq[6:]}"
    db.execute("delete from bbsm where rq=?", [rq])

    def get_mg(row: int, col: int) -> str:
        for r1, r2, c1, c2 in merged_cells:
            if r1 <= row < r2 and c1 <= col < c2:
                return data[r1][c1]
        return ""

    for r, row in enumerate(data[1:], 1):
        row = list(map(lambda x: x.strip() if isinstance(x, str) else x, row[1:10]))
        if any(row[1:4]):
            for c in range(min(9, len(row))):
                if not row[c]:
                    row[c] = get_mg(r, c + 1)
            if isinstance(row[1], (int, float)):
                row[1] = f"{int(row[1]):04d}"
            yield rq, *row, endate(row[-3])


@db.tran
def load(path):
    "读取文件数据"
    db.load("bbsm", 11, read(path), clear=False, print_result=True)
