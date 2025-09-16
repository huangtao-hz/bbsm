# 项目：   版本验收
# 模块：   导出本人内容
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-10-12 14:42

from . import Path
from bbsm import db
from orange import R

XuHao = R / (r"^(\d+\.)", "M")
query_sql = """
select distinct a.xmbh,a.xmjl,a.csjl,a.xrtcr,ifnull(b.xmmc,"")
from ysnr a
left join (select xmbh,max(xmmc)as xmmc from xqmx group by xmbh) b on a.xmbh=b.xmbh
where a.ysry like ? and a.tcrq=?
"""


def export_brnr():
    "以 .md 的格式导出本人的验收内容，方便打印验收"
    db.attach("xqxm", "xqxm")
    rq = db.fetchvalue("select max(tcrq)from ysnr")
    print("当前版本日期：", rq)
    s = [f"# 版本验收 {rq}", ""]
    for xmbh, xmjl, csjl, xrtcr, xmmc in db.fetch(query_sql, ["%黄涛%", rq]):
        s.append(f"## {xmbh} {xmmc}")
        s.append(f"> 项目经理：{xmjl}")
        s.append(f"> 测试经理：{csjl}")
        # s.append(f'> 需求名称：{xqmc}')
        s.append(f"> 需求提出人：{xrtcr}")
        for gnmc, gngs, cslxr in db.fetch(
            "select gnmc,gngs,cslxr from ysnr where ysry like ? and tcrq=? and xmbh=?",
            ["%黄涛%", rq, xmbh],
        ):
            s.append(f"### {gnmc}")
            cslxr = cslxr.replace("\n", "")
            s.append(f"> 测试联系人：{cslxr}")
            s.append(XuHao / gngs % (lambda x: x.groups()[0] + " "))
    root = Path("E:/工作笔记/版本验收")
    root.ensure()
    (root / f"版本验收 {rq}.md").text = "\r\n".join(s)
    db.detach("xqxm")
    print((root / f"版本验收 {rq}.md").name, "导出文件完成！")
