# 项目：   版本说明
# 模块：   导入数据模块
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2021-07-17 20:01


from orange import HOME, Path, R, datetime, extract, suppress
from xlrd3 import open_workbook
from bbsm import db
from bbsm import endate


def read(path: Path = None, file_contents=None):
    "读取版本说明文件"
    header1 = "序号,系统或项目,交易码,交易名称,测试内容,优化原因,验证机构,要求完成时间,验证要求,联系人"
    header2 = "序号,系统或项目,交易码及交易名称,测试内容,优化原因,验证网点,要求完成时间,验证要求,联系人"
    header3 = "序号,系统或项目,交易码,交易名称,优化内容,优化原因,验证网点,要求完成时间,验证要求,联系人"
    header4 = "序号,系统或项目,交易码,交易名称,优化内容,优化原因,验证机构,要求完成时间,验证要求,联系人"
    with open_workbook(filename=path, file_contents=file_contents) as book:
        sheet = book.sheet_by_index(0)
        # sheet = first(book if book else Path(path).worksheets)
        data = sheet._cell_values
        rq = extract(sheet.name.replace("-", ""), r"\d{8}")
        if path:
            rq2 = extract(path.pname, r"\d{8}")
            if rq != rq2:
                raise Exception(f"文件名中日期 {rq2} 与工作表中日期 {rq} 不一致")
        if ",".join(filter(None, data[0][:10])) not in (
            header1,
            header2,
            header3,
            header4,
        ):
            raise Exception("表头不一致")

        rq = f"{rq[:4]}-{rq[4:6]}-{rq[6:]}"
        db.execute("delete from bbsm where rq=?", [rq])
        merged_cells = sheet.merged_cells

        def get_mg(row: int, col: int) -> str:
            for r1, r2, c1, c2 in merged_cells:
                if r1 <= row < r2 and c1 <= col < c2:
                    return data[r1][c1]

        for r, row in enumerate(data[1:], 1):
            row = list(row[1:10])
            if any(row):
                for c in range(min(9, len(row))):
                    if not row[c]:
                        row[c] = get_mg(r, c + 1)
                if isinstance(row[1], (int, float)):
                    row[1] = f"{int(row[1]):04d}"
                yield rq, *row, endate(row[-3])


@suppress
def load(path: Path):
    ver = extract(path.pname, R / r"\d{8}")
    with db:
        db.lcheck("bbsm", path.name, path.mtime, ver)
        print(path.name, end="\t")
        db.load("bbsm", 11, data=read(path), clear=False, print_result=True)


def loadall():
    "按文件导入"
    ROOT = HOME / "Documents/参数备份/投产版本说明"
    for path in ROOT.glob("*版本说明????????.xlsx"):
        if "汇总" not in path.pname:
            load(path)


def load_all():
    "从 zip 文件中批量导入"
    from zipfile import ZipFile

    zfile = Path("~/Downloads/投产版本说明.zip")
    with ZipFile(zfile) as zf:

        @suppress
        @db.tran
        def load(fileinfo):
            name = Path(fileinfo.filename).pname
            if "汇总" in name:  # 忽略包含汇总的文件
                return
            mtime = datetime(*fileinfo.date_time) % "%F %T"
            ver = extract(name, R / r"\d{8}")
            db.lcheck("bbsm", name, mtime, ver)
            print(name, end="\t")
            with zf.open(fileinfo) as f:
                db.load(
                    "bbsm",
                    11,
                    data=read(None, f.read()),
                    clear=False,
                    print_result=True,
                )

        for fileinfo in zf.filelist:
            if not (fileinfo.flag_bits & 0x0800):
                fileinfo.filename = fileinfo.filename.encode("cp437").decode("gbk")
                zf.NameToInfo[fileinfo.filename] = fileinfo
            load(fileinfo)
