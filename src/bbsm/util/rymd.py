# 项目：   投产版本说明
# 模块：   人员模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2024-05-07 08:18

from bbsm import db
from orange import Path, slicer, suppress


@suppress
@db.tran
def load_rymd():
    """导入人员名单"""
    path = Path("~/Documents/版本说明").find("运营管理部人员名单.xlsx")
    if path:
        print("导入人员名单：", path.pname)
        db.lcheck("rymd", path, path.mtime)
        db.load(
            "rymd",
            3,
            path.read_sheet(slicer(1, 4), sheet=0, start_row=2),
            clear=True,
            print_result=True,
        )


def get_zg(name):
    "返回需求人员对应的主管"
    names = name.split("、")
    zg = db.fetchvalue(
        f"select group_concat(distinct zg) from rymd where xm in ({','.join(['?'] * len(names))}) ",
        names,
    )
    if isinstance(zg, str):
        return zg and zg.replace(",", "、")
    else:
        return ""
