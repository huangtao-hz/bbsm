# 项目：   版本验收内容
# 模块：   版本验收
# 作者：   黄涛
# License: GPL
# Email:   huangtao.sh@icloud.com
# 创建：2023-11-10 14:50

from . import loadfile, export, report
from orange import command, arg


@command(description='验收版本处理程序')
@arg('-l', '--load', action='store_true', help='导入版本内容')
@arg('-e', '--export', action='store_true', help='导出本人验收内容')
@arg('-r', '--report', action='store_true', help='报告版本验收内容的提交情况')
def main(**options):
    if options.get('load') or options.get('export'):
        loadfile.loadfile()
    if options.get('export'):
        export.export_brnr()
    if options.get('report'):
        report.report()


if __name__ == "__main__":
    main()
