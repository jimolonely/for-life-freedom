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


def format_value_percent(val):
    if val:
        return '%.2f%%' % (val * 100)
    return '0'


def col_width(val):
    """计算excel里列的宽度，根据val自适应"""
    return 256 * (len(str(val)) + 1) * 2


def pure_val(v):
    return v if v else 0


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

    def __init__(self, codes, target, from_year, end_year, file_name='分析报告'):
        self.codes = codes
        self.target = target
        assert target in codes
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
        self.step_06()
        self.step_07()
        self.step_08()
        self.wb.save('{}.xlsx'.format(self.file_name))

    def step_08(self):
        log.info('开始行业地位分析...')
        sheet = self.wb.add_sheet('08行业地位', cell_overwrite_ok=True)
        start_row = 0
        for code in self.codes:
            sheet.write(start_row, 0, '行业地位分析')
            sheet.write(start_row, 1, '科目名称')
            sheet.write(start_row + 1, 1, '应付票据及应付账款')
            sheet.write(start_row + 2, 1, '预收款项')
            sheet.write(start_row + 3, 1, '应收票据及应收账款')
            sheet.write(start_row + 4, 1, '预付款项')
            sheet.write(start_row + 5, 1, '无偿占有上下游资金')
            # 合并单元格
            sheet.write_merge(start_row + 1, start_row + 5, 0, 0, self.name_map[code])
            col = 2
            for year in range(self.from_year, self.end_year):
                sheet.col(col).width = col_width(123456789.12345)
                sheet.write(start_row, col, str(year))
                bp_and_ap = pure_val(self.data[code]['asset'][year]['bp_and_ap'][0])
                pre_recv = pure_val(self.data[code]['asset'][year]['pre_receivable'][0])
                ar_and_br = pure_val(self.data[code]['asset'][year]['ar_and_br'][0])
                pre_pay = pure_val(self.data[code]['asset'][year]['pre_payment'][0])
                occupy = (bp_and_ap + pre_recv) - (ar_and_br + pre_pay)
                sheet.write(start_row + 1, col, format_value(bp_and_ap))
                sheet.write(start_row + 2, col, format_value(pre_recv))
                sheet.write(start_row + 3, col, format_value(ar_and_br))
                sheet.write(start_row + 4, col, format_value(pre_pay))
                sheet.write(start_row + 5, col, format_value(occupy))
                col += 1

            # 下一家公司位置
            start_row += 8

    def step_07(self):
        log.info('开始偿债风险分析...')
        sheet = self.wb.add_sheet('07偿债风险', cell_overwrite_ok=True)
        sheet.write(0, 0, '偿债风险分析')
        sheet.write(0, 1, '科目名称')
        sheet.write(1, 1, '短期借款')
        sheet.write(2, 1, '其中：应付利息')
        sheet.write(3, 1, '一年内到期的非流动负债')
        sheet.write(4, 1, '长期借款')
        sheet.write(5, 1, '长期应付款')
        sheet.write(6, 1, '小计')
        sheet.write(7, 1, '货币资金')
        code = self.target
        # 合并单元格
        sheet.write_merge(1, 7, 0, 0, self.name_map[code])
        col = 2
        for year in range(self.from_year, self.end_year):
            sheet.col(col).width = col_width(123456789.12345)
            sheet.write(0, col, str(year))
            st_loan_ = pure_val(self.data[code]['asset'][year]['st_loan'][0])
            interest_payable_ = pure_val(self.data[code]['asset'][year]['interest_payable'][0])
            noncurrent_liab_due_in1y = pure_val(self.data[code]['asset'][year]['noncurrent_liab_due_in1y'][0])
            lt_loan_ = pure_val(self.data[code]['asset'][year]['lt_loan'][0])
            lt_payable_ = pure_val(self.data[code]['asset'][year]['lt_payable'][0])
            sheet.write(1, col, format_value(st_loan_))
            sheet.write(2, col, format_value(interest_payable_))
            sheet.write(3, col, format_value(noncurrent_liab_due_in1y))
            sheet.write(4, col, format_value(lt_loan_))
            sheet.write(5, col, format_value(lt_payable_))
            sheet.write(6, col,
                        format_value(st_loan_ + interest_payable_ + noncurrent_liab_due_in1y + lt_loan_ + lt_payable_))
            sheet.write(7, col, format_value(self.data[code]['asset'][year]['currency_funds'][0]))
            col += 1

    def step_06(self):
        log.info('开始资产负债率分析...')
        sheet = self.wb.add_sheet('06资产负债率', cell_overwrite_ok=True)
        row = 1
        sheet.write(0, 0, '资产负债率')
        for code in self.codes:
            col = 1
            sheet.write(row, 0, self.name_map[code])
            sheet.write(row + 1, 0, '>资产负债率')
            for year in range(self.from_year, self.end_year):
                total_liab_ = self.data[code]['asset'][year]['total_liab'][0]
                total_assets_ = self.data[code]['asset'][year]['total_assets'][0]
                sheet.col(col).width = col_width(total_assets_)
                sheet.write(0, col, str(year))
                sheet.write(row, col, '{}/{}'.format(total_liab_, total_assets_))
                sheet.write(row + 1, col, format_value_percent(total_liab_ / total_assets_))
                col += 1
            row += 2

    def step_05(self):
        log.info('开始总资产分析...')
        sheet = self.wb.add_sheet('05总资产', cell_overwrite_ok=True)
        row = 1
        sheet.write(0, 0, '总资产')
        for code in self.codes:
            col = 1
            sheet.write(row, 0, self.name_map[code])
            sheet.write(row + 1, 0, '增长率')
            for year in range(self.from_year, self.end_year):
                sheet.col(col).width = 256 * 20
                sheet.write(0, col, str(year))
                sheet.write(row, col, format_value(self.data[code]['asset'][year]['total_assets'][0]))
                sheet.write(row + 1, col, format_value_percent(self.data[code]['asset'][year]['total_assets'][1]))
                col += 1
            row += 2


if __name__ == '__main__':
    g = GenerateReport(['SZ000895', 'SZ002726', 'SZ002840'], 'SZ000895', 2015, 2019)
    g.execute_all()
