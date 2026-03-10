# 项目：版本说明
# 模块：生成笔记模块
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2022-11-09 22:19
# 修改：2022-11-12 21:18 新增导出 markdown 功能
# 修订：2023-04-17 17:12 fix bugs
# 修订：2025-09-09 14:16 支持 5 位新交易码

import sys

from orange import Path, R, groupby

from bbsm import db


def publish():
    """
    将版本说明导出为 markdown 文件，方便查阅和打印。
    """
    ReplacChar = R / r"""[\/?*]"""  # 文件名中不允许包含的字符
    No = R / r"(\d{1,2})[.、](.*?)"  # 序号
    if sys.platform == "darwin":  # macOS 平台的目录
        path = Path(
            "/Users/huangtao/Library/Mobile Documents/iCloud~md~obsidian/Documents/Huangtao/版本说明"
        )
    else:  # Windows 平台对应目录
        path = Path("~/版本说明")
    path.ensure()

    file = path / "0000-版本说明.md"
    jy_data = {}
    updated_date = "0000-01-01"
    if file:
        data = file.read_bytes()
        lines = data.decode("utf8").splitlines()
        updated_date = lines[0][-10:]
        print("已更新到：", updated_date)
        for row in lines[1:]:
            jy = row[2:-2].split("-")[0]
            jy_data[jy] = row[2:-2]

    lated_date = db.fetchvalue("select max(rq)from bbsm")
    assert lated_date is not None and isinstance(lated_date, str)
    print(updated_date, lated_date)
    if updated_date >= lated_date:
        print("无需更新")
        return
    sql = (
        "select a.jym,jymc,nr,lxr,yhyy,rq from bbsm a left join "
        '(select distinct jym from bbsm where jym<>"" and rq>?) b on a.jym=b.jym '
        "where b.jym is not null "
        "order by a.jym,rq desc "
    )

    contents = [f"更新时间：{lated_date}"]

    def read():
        for jym, *row in db.fetch(sql, [updated_date]):  # 搜索已更新日期之后的数据
            if jym.upper() == "F4" or R / r"\d{4,5}" == jym:
                yield jym, *row

    for jym, data in groupby(read(), 0):
        jymc = data[0][1]
        filename = f"{jym}-{ReplacChar / jymc % ''}"
        old_file = jy_data.get(jym, None)
        if old_file:
            if old_file != filename:
                (path / f"{old_file}.md").unlink()
                print("删除文件：", old_file)
        contents.append(f"[[{filename}]]")
        s = []
        for _, __, nr, lxr, yhyy, rq in data:
            s.append(f"\n## {rq}（{lxr if lxr else ''} {yhyy}）")
            for r in nr.splitlines():
                m = No.fullmatch(r)
                if m:
                    m = m.groups()
                    s.append(f"{m[0]}. {m[1]}")
                else:
                    s.append(f"\n{r}")
        (path / f"{filename}.md").lines = s

    file.lines = contents
    print("生成文件成功！")
