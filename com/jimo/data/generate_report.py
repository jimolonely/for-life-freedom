import json
import logging
import xlwt
import locale
import codecs


def get_logger(name):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('jimo_' + name)
    return logger


log = get_logger('info.log')


def format_value(val):
    if val:
        locale.setlocale(locale.LC_ALL, '')
        return locale.format_string("%.2f", val, True)
    return '0'


class GenerateReport:
    """
    分为23个步骤
    因为涉及几家公司对比，所以需要同时加载几家公司的数据
    输入对比的几家公司code，起止年份
    输出23个步骤的excel表格
    处理过程：
    1.根据code加载data目录下的数据，每个公司3个报表数据
    {
        asset: {
            "2019": {k:v},
            "2018": {k:v},
            ...
        },
        cash: {},
        profit: {}
    }
    2.遍历每一年的数据，处理过程是一样的
    3.比如以资产总额为例：求资产总额及其增长率，一个公司分2行，第一行为资产总额，第二行为增长率，列为年份
    for year in range(from,to):
        sh.write(1,i,a['total_assets'][0][year])
        i+=1
        # 求增长率
        if i > 0
    """

    def __init__(self, codes, from_year, end_year, file_name='分析报告'):
        self.codes = codes
        self.from_year = from_year
        self.end_year = end_year + 1
        self.file_name = file_name
        self.name_map = {}
        self.data = self.init_data()
        self.wb = xlwt.Workbook(encoding='utf-8')

    def init_data(self):
        data = {}
        for code in self.codes:
            one = {'asset': self.load_json_item(code, 'asset'),
                   'cash': self.load_json_item(code, 'cash'),
                   'profit': self.load_json_item(code, 'profit')}
            data[code] = one
        return data

    def load_json_item(self, code, name):
        item = {}
        with codecs.open('data/{}.json'.format(code), 'r', encoding='utf-8') as f:
            one_obj = json.load(f)
        for d in one_obj[name]:
            # 取出年份为key
            item[int(d['report_name'][:4])] = d
        self.name_map[code] = one_obj['name']
        return item

    def execute_all(self):
        # TODO 23 step
        self.step_05()
        self.wb.save('{}.xlsx'.format(self.file_name))

    def step_05(self):
        log.info('开始总资产分析...')
        sheet = self.wb.add_sheet('总资产', cell_overwrite_ok=True)
        row = 1
        sheet.write(0, 0, '总资产')
        for code in self.codes:
            col = 1
            sheet.write(row, 0, self.name_map[code])
            sheet.write(row + 1, 0, '增长率')
            for year in range(self.from_year, self.end_year):
                sheet.write(0, col, str(year))
                sheet.write(row, col, format_value(self.data[code]['asset'][year]['total_assets'][0]))
                sheet.write(row + 1, col, format_value(self.data[code]['asset'][year]['total_assets'][1]))
                col += 1
            row += 2


if __name__ == '__main__':
    g = GenerateReport(['SZ000895', 'SZ002726', 'SZ002840'], 2015, 2019)
    g.execute_all()
