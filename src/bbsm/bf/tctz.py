# 项目：   版本说明
# 模块：   投产通知
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-04-23 09:16


from orange.word import Document
from orange import Path, datetime
from bbsm import db


def tctz(path: Path, tcrq: str):
    "下发投产通知"
    rq = datetime(tcrq)
    body = f"""总行决定于{rq:%x}晚对数智综合运营系统等系统进行升级。具体要求如下：
具体升级内容详见《版本说明{rq:%Y%m%d}》（附件），请各网点营业主管组织柜员认真学习升级内容，掌握升级内容。柜面人员可随时在柜面系统按“Ctrl + Shift + H”热键查询版本更新内容。
执行中遇有问题，请及时与总行联系，联系人：丁涵旻，联系电话：0571-88267995。

附件：版本说明{rq:%Y%m%d}

"""
    doc = Document()
    doc.add_title(f"关于下发系统版本说明（{rq:%Y%m%d}）的通知")
    year = rq % "%Y"
    wh = db.fetchvalue(
        "select count(distinct rq) from bbsm where rq like ?", [f"{year}%"]
    )
    doc.add_wenhao(f"浙商银运管版〔{year}〕{wh}号")
    doc.add_zsjg("境内各分行")
    doc.add_para(body)
    doc.add_fwjg("总行运营管理部")
    # p.style.aligment=WD_ALIGN_PARAGRAPH.CENTER
    # p.style.font.size = 12

    doc.save(str(path))
