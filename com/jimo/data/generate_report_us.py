import codecs
import json
import locale
import logging

import xlwt


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


def a_or_b(a, b):
    x = a if a else b
    return x if x else 0


def load_json(file):
    with codecs.open(file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_term_map():
    return {'asset': load_json('资产负债表术语对应表us.json'), 'profit': load_json('利润表术语对应表us.json'),
            'cash': load_json('现金流量表术语对应表us.json')}


class GenerateReport:
    """
    分为23个步骤
    因为涉及几家公司对比，所以需要同时加载几家公司的数据
    输入对比的几家公司code，起止年份
    输出23个步骤的excel表格
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
        self.term_map = load_term_map()
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

    def write_one(self, title, items, get_value, start_row=0, code=None, sheet=None, extra_cols=None):
        """
        单个目标公司分析模板
        :param extra_cols: 额外的列，{'列名':[值数组]}
        :param sheet: sheet实例
        :param code: 要处理的公司
        :param title: 分析项
        :param items: 分析类目列表['','']
        :param get_value: 函数，自定义返回数据，传入年份
        :param start_row: excel中的起始行
        :return:
        """
        if sheet is None:
            sheet = self.wb.add_sheet(title, cell_overwrite_ok=True)
        sheet.write(start_row, 0, title)
        sheet.write(start_row, 1, '科目名称')
        i = 1
        for item in items:
            sheet.write(start_row + i, 1, item)
            i += 1
        if code is None:
            code = self.target
        # 合并单元格
        sheet.write_merge(start_row + 1, start_row + len(items), 0, 0, self.name_map[code])
        col = 2
        for year in range(self.from_year, self.end_year):
            sheet.write(start_row, col, str(year))
            total_assets_ = pure_val(self.data[code]['asset'][year]['total_assets'][0])
            sheet.col(col).width = col_width(total_assets_)
            values = get_value(year, code)
            row = 1
            for v in values:
                sheet.write(start_row + row, col, v)
                row += 1
            col += 1
        if extra_cols is not None:
            row = 1
            for k in extra_cols.keys():
                sheet.write(start_row, col, k)
                for v in extra_cols[k]:
                    sheet.write(start_row + row, col, v)
                    row += 1
                col += 1

    def write_many(self, title, items, get_value):
        """
        多个目标公司分析模板
        :param title: 分析项
        :param items: 分析类目列表['','']
        :param get_value: 函数，自定义返回数据，传入年份
        :return:
        """
        sheet = self.wb.add_sheet(title, cell_overwrite_ok=True)
        start_row = 0
        for code in self.codes:
            self.write_one(title, items, get_value, start_row, code, sheet)
            start_row += len(items) + 3

    def execute_all(self):
        # 23 step
        self.step_03()
        self.step_05()
        self.step_06()
        self.step_07()
        self.step_08()
        self.step_09()
        self.step_10()
        self.step_11()
        self.step_12()
        self.step_13()
        self.step_14()
        self.step_15()
        self.step_16()
        self.step_17()
        self.step_18()
        self.step_19()
        self.step_20()
        self.step_21()
        self.step_22()
        self.step_23()
        self.wb.save('{}.xls'.format(self.file_name))

    def step_23(self):
        log.info('公司稳定性分析...')
        items = ['现金及现金等价物的净增加额', '分红金额', '现金及现金等价物的净增加额+当年分红金额']

        def get_value(year, code):
            net_increase_in_cce = pure_val(self.data[code]['cash'][year]['increase_in_cce'][0])
            dividend = abs(pure_val(self.data[code]['cash'][year]['dividend_paid'][0]))

            return [format_value(net_increase_in_cce), format_value(dividend),
                    format_value(net_increase_in_cce + dividend)]

        self.write_one('23公司稳定性分析', items, get_value)

    def step_22(self):
        log.info('公司类型分析...')
        items = ['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额', '类型']

        def ng(v):
            return '正' if v > 0 else '负'

        def get_value(year, code):
            ncf_from_oa = pure_val(self.data[code]['cash'][year]['net_cash_provided_by_oa'][0])
            ncf_from_ia = pure_val(self.data[code]['cash'][year]['net_cash_used_in_ia'][0])
            ncf_from_fa = pure_val(self.data[code]['cash'][year]['net_cash_used_in_fa'][0])

            return [format_value(ncf_from_oa), format_value(ncf_from_ia), format_value(ncf_from_fa),
                    '{}{}{}'.format(ng(ncf_from_oa), ng(ncf_from_ia), ng(ncf_from_fa))]

        self.write_one('22公司类型分析', items, get_value)

    def step_21(self):
        log.info('分红分析')
        items = ['支付股息', '净利润', '分红率']

        def get_value(year, code):
            dividend_paid = abs(pure_val(self.data[code]['cash'][year]['dividend_paid'][0]))
            net_profit = pure_val(self.data[code]['profit'][year]['net_income'][0])
            return [format_value(dividend_paid), format_value(net_profit),
                    format_value_percent(dividend_paid / net_profit)]

        self.write_one('21分红分析', items, get_value)

    def step_20(self):
        log.info('未来成长能力分析...')
        items = ['投资活动产生的现金流量净额', '经营活动产生的现金流量净额', '比值']

        def get_value(year, code):
            cash_paid_for_assets = pure_val(self.data[code]['cash'][year]['net_cash_used_in_ia'][0])
            ncf_from_oa = pure_val(self.data[code]['cash'][year]['net_cash_provided_by_oa'][0])

            return [format_value(cash_paid_for_assets), format_value(ncf_from_oa),
                    format_value_percent(cash_paid_for_assets / ncf_from_oa)]

        self.write_one('20未来成长能力分析', items, get_value)

    def step_19(self):
        log.info('造血能力分析...')
        items = ['经营活动产生的现金流量净额', '折旧与摊销', '分配股利、利润或偿付利息支付的现金', '小计', '差额']

        def get_value(year, code):
            ncf_from_oa = pure_val(self.data[code]['cash'][year]['net_cash_provided_by_oa'][0])
            # 折旧和摊销
            depreciation_and_amortization = pure_val(self.data[code]['cash'][year]['depreciation_and_amortization'][0])
            cash_paid_of_distribution = abs(pure_val(self.data[code]['cash'][year]['dividend_paid'][0]))
            sum_s = depreciation_and_amortization + cash_paid_of_distribution
            return [format_value(ncf_from_oa),
                    format_value(depreciation_and_amortization), format_value(cash_paid_of_distribution),
                    format_value(sum_s), format_value(ncf_from_oa - sum_s)]

        self.write_one('19造血能力分析', items, get_value)

    def step_18(self):
        log.info('获利能力(ROE)分析...')
        items = ['归属于母公司股东的综合收益总额', '增长率', '净利润', '所有者权益', '净资产收益率(ROE)']

        def get_value(year, code):
            total_compre_income_atsopc = pure_val(self.data[code]['profit'][year]['total_compre_income_atcss'][0])
            total_compre_income_atsopc_rate = pure_val(self.data[code]['profit'][year]['total_compre_income_atcss'][1])
            net_profit = pure_val(self.data[code]['profit'][year]['net_income'][0])
            total_holders_equity = pure_val(self.data[code]['asset'][year]['total_holders_equity'][0])
            total_holders_equity_last = pure_val(self.data[code]['asset'][year - 1]['total_holders_equity'][0])
            return [format_value(total_compre_income_atsopc), format_value_percent(total_compre_income_atsopc_rate),
                    format_value(net_profit), format_value(total_holders_equity),
                    format_value_percent(net_profit / (total_holders_equity + total_holders_equity_last) * 2)]

        self.write_one('18获利能力(ROE)分析', items, get_value)

    def step_17(self):
        log.info('净利润含金量分析...')
        items = ['净利润', '经营活动产生的现金流量净额', '净利润现金比率']

        def get_value(year, code):
            net_profit = pure_val(self.data[code]['profit'][year]['net_income'][0])
            ncf_from_oa = pure_val(self.data[code]['cash'][year]['net_cash_provided_by_oa'][0])
            return [format_value(net_profit), format_value(ncf_from_oa), format_value_percent(ncf_from_oa / net_profit)]

        # 附加的一列求和
        # key:标题行，value：数组值
        code1 = self.target
        sum_net_profit = 0
        sum_ncf_from_oa = 0
        for year1 in range(self.from_year, self.end_year):
            net_profit1 = pure_val(self.data[code1]['profit'][year1]['net_income'][0])
            ncf_from_oa1 = pure_val(self.data[code1]['cash'][year1]['net_cash_provided_by_oa'][0])
            sum_net_profit += net_profit1
            sum_ncf_from_oa += ncf_from_oa1
        d_sum = {'合计': [format_value(sum_net_profit), format_value(sum_ncf_from_oa),
                        format_value_percent(sum_ncf_from_oa / sum_net_profit)]}

        self.write_one('17净利润含金量分析', items, get_value, extra_cols=d_sum)

    def step_16(self):
        log.info('盈利和利润质量分析...')
        items = ['营业收入', '营业利润', '利润总额', '营业利润率', '营业利润/利润总额']

        def get_value(year, code):
            revenue = pure_val(self.data[code]['profit'][year]['revenue'][0])
            op = pure_val(self.data[code]['profit'][year]['operating_income'][0])
            profit_total_amt = pure_val(self.data[code]['profit'][year]['income_from_co_before_it'][0])
            return [format_value(revenue), format_value(op), format_value(profit_total_amt),
                    format_value_percent(op / revenue), format_value_percent(op / profit_total_amt)]

        self.write_many('16盈利和利润质量分析', items, get_value)

    def step_15(self):
        log.info('成本管控力分析...')
        items = ['营业收入', '市场、销售和管理费用', '研发费用', '费用率', '费用率/毛利率']

        def get_value(year, code):
            operating_cost = pure_val(self.data[code]['profit'][year]['sales_cost'][0])
            revenue = pure_val(self.data[code]['profit'][year]['revenue'][0])
            sales_fee = pure_val(self.data[code]['profit'][year]['marketing_selling_etc'][0])
            rad_cost = pure_val(self.data[code]['profit'][year]['rad_expenses'][0])
            fee_rate = (sales_fee + rad_cost) / revenue
            fee_rate_divide_margin_rate = fee_rate / (1 - operating_cost / revenue)
            return [format_value(revenue), format_value(sales_fee), format_value(rad_cost),
                    format_value_percent(fee_rate), format_value_percent(fee_rate_divide_margin_rate)]

        self.write_many('15成本管控力分析', items, get_value)

    def step_14(self):
        log.info('竞争力分析...')
        items = ['营业收入', '营业成本', '毛利率']

        def get_value(year, code):
            operating_cost = pure_val(self.data[code]['profit'][year]['sales_cost'][0])
            revenue = pure_val(self.data[code]['profit'][year]['revenue'][0])
            return [format_value(operating_cost), format_value(revenue),
                    format_value_percent(1 - operating_cost / revenue)]

        self.write_many('14竞争力分析', items, get_value)

    def step_13(self):
        log.info('行业地位和成长能力分析...')
        items = ['销售商品、提供劳务收到的现金', '营业收入', '销售商品、提供劳务收到的现金/营业收入', '营业收入增长率']

        def get_value(year, code):
            cash_received_of_sales_service = pure_val(
                self.data[code]['cash'][year]['net_cash_provided_by_oa'][0])
            revenue = pure_val(self.data[code]['profit'][year]['revenue'][0])
            revenue_growth_rate = pure_val(self.data[code]['profit'][year]['revenue'][1])
            return [format_value(cash_received_of_sales_service), format_value(revenue),
                    format_value_percent(cash_received_of_sales_service / revenue),
                    format_value_percent(revenue_growth_rate)]

        self.write_one('13行业地位和成长能力分析', items, get_value)

    def step_12(self):
        log.info('现金流量表异常分析...')
        self.exp_analyze('12现金流量表异常', 'cash')

    def step_11(self):
        log.info('利润表异常分析...')
        self.exp_analyze('11利润表异常', 'profit')

    def step_10(self):
        log.info('开始主业专注度分析...')
        sheet = self.wb.add_sheet('10主业专注度', cell_overwrite_ok=True)
        sheet.write(0, 0, '主业专注度分析')
        sheet.write(0, 1, '科目名称')
        sheet.write(1, 1, '以公允价值计量且其变动计入当期损益的金融资产/交易性金融资产')
        sheet.write(2, 1, '可供出售金融资产')
        sheet.write(3, 1, '持有至到期投资')
        sheet.write(4, 1, '投资性房地产')
        sheet.write(5, 1, '长期股权投资')
        sheet.write(6, 1, '无形资产净额')
        sheet.write(7, 1, '与主业无关的投资小计')
        sheet.write(8, 1, '总资产')
        sheet.write(9, 1, '与主业无关的投资占总资产的比率')
        code = self.target
        # 合并单元格
        sheet.write_merge(1, 9, 0, 0, self.name_map[code])
        col = 2
        for year in range(self.from_year, self.end_year):
            sheet.write(0, col, str(year))
            total_assets_ = pure_val(self.data[code]['asset'][year]['total_assets'][0])
            sheet.col(col).width = col_width(total_assets_)
            tradable_fnncl_assets = 0
            salable_financial_assets = 0
            held_to_maturity_invest = 0
            invest_property = 0
            lt_equity_invest = pure_val(self.data[code]['asset'][year]['equity_and_othr_invest'][0])
            net_intangible_assets = pure_val(self.data[code]['asset'][year]['net_intangible_assets'][0])
            other_invest_sum = tradable_fnncl_assets + salable_financial_assets + held_to_maturity_invest \
                               + invest_property + lt_equity_invest + net_intangible_assets
            sheet.write(1, col, format_value(tradable_fnncl_assets))
            sheet.write(2, col, format_value(salable_financial_assets))
            sheet.write(3, col, format_value(held_to_maturity_invest))
            sheet.write(4, col, format_value(invest_property))
            sheet.write(5, col, format_value(lt_equity_invest))
            sheet.write(6, col, format_value(net_intangible_assets))
            sheet.write(7, col, format_value(other_invest_sum))
            sheet.write(8, col, format_value(total_assets_))
            sheet.write(9, col, format_value_percent(other_invest_sum / total_assets_))
            col += 1

    def step_09(self):
        log.info('开始公司轻重分析...')
        sheet = self.wb.add_sheet('09轻重分析', cell_overwrite_ok=True)
        start_row = 0
        for code in self.codes:
            sheet.write(start_row, 0, '轻重分析')
            sheet.write(start_row, 1, '科目名称')
            sheet.write(start_row + 1, 1, '固定资产')
            sheet.write(start_row + 2, 1, '在建工程')
            sheet.write(start_row + 3, 1, '工程物资')
            sheet.write(start_row + 4, 1, '小计')
            sheet.write(start_row + 5, 1, '总资产')
            sheet.write(start_row + 6, 1, '小计/总资产')
            # 合并单元格
            sheet.write_merge(start_row + 1, start_row + 6, 0, 0, self.name_map[code])
            col = 2
            for year in range(self.from_year, self.end_year):
                total_assets_ = pure_val(self.data[code]['asset'][year]['total_assets'][0])
                sheet.col(col).width = col_width(total_assets_)
                sheet.write(start_row, col, str(year))
                fixed_asset = pure_val(self.data[code]['asset'][year]['gross_property_plant_and_equip'][0])
                construction_in_process_sum = 0
                construction_in_process = 0
                project_goods_and_material = 0

                final_fixed_asset = fixed_asset
                final_construction = a_or_b(construction_in_process, construction_in_process_sum)
                sum_asset = final_fixed_asset + final_construction + project_goods_and_material

                sheet.write(start_row + 1, col, format_value(final_fixed_asset))
                sheet.write(start_row + 2, col, format_value(final_construction))
                sheet.write(start_row + 3, col, format_value(project_goods_and_material))
                sheet.write(start_row + 4, col, format_value(sum_asset))
                sheet.write(start_row + 5, col, format_value(total_assets_))
                sheet.write(start_row + 6, col, format_value_percent(sum_asset / total_assets_))
                col += 1

            # 下一家公司位置
            start_row += 9

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
            sheet.write(start_row + 6, 1, '应收账款/总资产')
            # 合并单元格
            sheet.write_merge(start_row + 1, start_row + 5, 0, 0, self.name_map[code])
            col = 2
            for year in range(self.from_year, self.end_year):
                total_assets_ = pure_val(self.data[code]['asset'][year]['total_assets'][0])
                sheet.col(col).width = col_width(total_assets_)
                sheet.write(start_row, col, str(year))
                account_receivable = pure_val(self.data[code]['asset'][year]['net_receivables'][0])
                bp_and_ap = pure_val(self.data[code]['asset'][year]['accounts_payable'][0])
                pre_recv = 0
                ar_and_br = pure_val(self.data[code]['asset'][year]['net_receivables'][0])
                pre_pay = pure_val(self.data[code]['asset'][year]['prepaid_expense'][0])
                occupy = (bp_and_ap + pre_recv) - (ar_and_br + pre_pay)
                sheet.write(start_row + 1, col, format_value(bp_and_ap))
                sheet.write(start_row + 2, col, format_value(pre_recv))
                sheet.write(start_row + 3, col, format_value(ar_and_br))
                sheet.write(start_row + 4, col, format_value(pre_pay))
                sheet.write(start_row + 5, col, format_value(occupy))
                sheet.write(start_row + 6, col, format_value_percent(account_receivable / total_assets_))
                col += 1

            # 下一家公司位置
            start_row += 9

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
            st_loan_ = pure_val(self.data[code]['asset'][year]['st_debt'][0])
            interest_payable_ = 0
            noncurrent_liab_due_in1y = 0
            lt_loan_ = pure_val(self.data[code]['asset'][year]['lt_debt'][0])
            lt_payable_ = 0
            sheet.write(1, col, format_value(st_loan_))
            sheet.write(2, col, format_value(interest_payable_))
            sheet.write(3, col, format_value(noncurrent_liab_due_in1y))
            sheet.write(4, col, format_value(lt_loan_))
            sheet.write(5, col, format_value(lt_payable_))
            sheet.write(6, col,
                        format_value(st_loan_ + interest_payable_ + noncurrent_liab_due_in1y + lt_loan_ + lt_payable_))
            sheet.write(7, col, format_value(self.data[code]['asset'][year]['cce'][0]))
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

    def step_03(self):
        log.info('资产负债表异常分析...')
        self.exp_analyze('03-04资产负债表异常', 'asset')

    def exp_analyze(self, title, report_type, ):
        sheet = self.wb.add_sheet('{}分析'.format(title), cell_overwrite_ok=True)
        sheet.write(0, 0, title)
        # 每一年占3列：异常项目,比例,改变率
        col = 1
        code = self.target
        for year in range(self.from_year, self.end_year):
            sheet.write_merge(0, 0, col, col + 1, str(year))
            total_assets_ = pure_val(self.data[code]['asset'][year]['total_assets'][0])
            sheet.col(col).width = col_width(total_assets_)
            one_year_data = self.data[code][report_type][year]
            sheet.write(1, col, '异常项')
            sheet.write(1, col + 1, '占总资产比例')
            sheet.write(1, col + 2, '同比增长')
            row = 2
            for k in one_year_data.keys():
                if one_year_data[k] is not None and isinstance(one_year_data[k], list):
                    val = pure_val(one_year_data[k][0])
                    rate = abs(pure_val(one_year_data[k][1]))
                    if val / total_assets_ > 0.03 and rate > 0.3:
                        sheet.write(row, col, self.term_map[report_type].get(k, '未知名称'))
                        sheet.write(row, col + 1, format_value_percent(val / total_assets_))
                        sheet.write(row, col + 2, format_value_percent(pure_val(one_year_data[k][1])))
                        row += 1
            col += 3


if __name__ == '__main__':
    # g = GenerateReport(['SZ000895', 'SZ002726', 'SZ002840'], 'SZ000895', 2015, 2019)
    # g = GenerateReport(['SZ300117', 'SZ002081', 'SZ002375'], 'SZ300117', 2015, 2019)
    g = GenerateReport(['CME'], 'CME', 2015, 2019)
    g.execute_all()
