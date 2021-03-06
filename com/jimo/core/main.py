import json
import re

import requests

iwencai_headers = {
    'Host': 'www.iwencai.com',
    'Origin': 'http://www.iwencai.com',
    'Referer': 'http://www.iwencai.com/',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
}

xueqiu_headers = {
    'Host': 'stock.xueqiu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
    'Cookie': 'xq_a_token=a664afb60c7036c7947578ac1a5860c4cfb6b3b5; '
              'xqat=a664afb60c7036c7947578ac1a5860c4cfb6b3b5; '
              'xq_r_token=01d9e7361ed17caf0fa5eff6465d1c90dbde9ae2; '
              'xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV'
              '4cCI6MTU4NTM2MjYwNywiY3RtIjoxNTgzNjgyNjI5MDgyLCJjaWQiOiJkOWQwbjRBWnVwIn0.'
              'nVT2cBhNGU9Hgs0JvEtoV8MagcYPVvaz6iXOF83DRC2AUW1vpsYqyuPsIUm7zNWN7N1kBrUr8NyC1OOT4kW'
              '_cf8yZ1KewXyjVntWdAZBwRSXdDrIC6zjjP1N8ARQyFepsaz8dHJlpTSangUWdC3qrLW7qKQGYS0OUUvd'
              'ILhnHGvOQrAmHeJWgN-8h4HT9BrpmlR9fErjIfn954_k7O-8yjiXTvTepMWt2MxtjREtiF6zMmZLppZpsBoGV5prsgbxaF'
              '-OYY8LhMSzLSndfZ_LjM9YN7QrIBA4VX_xn3vUICrBm2YvMGoglMeo7T-cOvQGU-Atw-q0BA78hd0NkCoMFg; '
              'u=941583682640528; cookiesu=831583682643721; device_id=24700f9f1986800ab4fcc880530dd0ed;'
              ' Hm_lvt_1db88642e346389874251b5a1eded6e3=1583682646; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1583682646'
}


def request_iwencai_stock_pick(condition):
    url = 'http://www.iwencai.com/unifiedwap/unified-wap/result/get-stock-pick'
    body = {
        'question': condition,
        'secondary_intent': 'hkstock',
        'perpage': 50
    }
    r = requests.post(url, data=body, headers=iwencai_headers)
    print(r.json())
    return r.json()


def request_iwencai_robot_api(question):
    url = 'http://www.iwencai.com/unifiedwap/unified-wap/result/get-robot-data' \
          '?source=Ths_iwencai_Xuangu&version=2.0&secondary_intent=hkstock'
    body = {
        'question': question,
        'add_info': {"urp": {"scene": 1, "company": 1, "business": 1}}
    }
    r = requests.post(url, data=body, headers=iwencai_headers)
    res = r.json()
    return res


class Stock:
    """股票实体"""

    def __init__(self, p_json):
        """json to stock:
        {'股票代码': '1928.HK', '股票简称': '金沙中国有限公司',
        '港股@净资产收益率roe[20141231]': 39.62617043379367,
        '港股@净资产收益率roe[20151231]': 24.99641609596813,
        '港股@净资产收益率roe[20161231]': 24.44577591372079,
        '港股@净资产收益率roe[20171231]': 35.32393124724548,
        '港股@净资产收益率roe[20181231]': 42.52665003402132,
        '港股@净利润现金含量占比[20141231]': 126.53938605112683,
        '港股@净利润现金含量占比[20151231]': 134.81836874571624,
        '港股@净利润现金含量占比[20161231]': 191.66666666666669,
        '港股@净利润现金含量占比[20171231]': 163.8178415470992,
        '港股@净利润现金含量占比[20181231]': 162.61333333333334,
        '港股@销售毛利率[20141231]': '58.4403',
        '港股@销售毛利率[20151231]': '61.2642',
        '港股@销售毛利率[20161231]': '62.0171',
        '港股@销售毛利率[20171231]': '62.0868',
        '港股@销售毛利率[20181231]': '60.4155',
        '港股@上市天数[20200306]': 3750,
        '港股@资产负债率[20141231]': '43.3417',
        '港股@资产负债率[20151231]': '45.7968',
        '港股@资产负债率[20161231]': '55.2267',
        '港股@资产负债率[20171231]': '57.3777',
        '港股@资产负债率[20181231]': '63.4351',
        '港股@归属于母公司所有者的净利润[20141231]': 19759992224,
        '港股@最新价': '34.700',
        '港股@最新涨跌幅': '-3.477', 'hqCode': 'HK1928', 'marketId': '177'}
        """
        self.code = ''
        self.name = ''
        # 供股及公开招股记录
        self.rights_issue = {}
        self.dividend_rate = []
        self.asset_liability = []
        self.gross_profit = []
        self.profit_cash_ratio = []
        self.roe = []
        # 股息TTM
        self.dividend = 0
        self.pe_ttm = 0
        self.eps = 0
        self.current_price = 0

        hq_code = re.sub(r'\D', '', p_json['hqCode'])
        self.code = hq_code.zfill(5)
        self.name = p_json['股票简称']
        print('当前正在获取{}（{}）的相关信息...'.format(self.name, self.code))
        for k in p_json:
            if 'roe' in k:
                self.roe.append((re.sub(r'\D', "", k), p_json[k]))
            elif '净利润现金含量占比' in k:
                self.profit_cash_ratio.append((re.sub(r'\D', '', k), p_json[k]))
            elif '毛利率' in k:
                self.gross_profit.append((re.sub(r'\D', '', k), p_json[k]))
            elif '资产负债率' in k:
                self.asset_liability.append((re.sub(r'\D', '', k), p_json[k]))

        self.get_dividend_rate()
        self.get_rights_issue()
        self.get_stock_detail()

    def get_dividend_rate(self):
        """
        1.获取归母净利润
        2.获取分红现金总额
        3.2/1得到每年分红率
        """
        res = request_iwencai_stock_pick(self.code + ' 2014到2018年净利润')
        data = res['data']['data'][0]
        d_profit = {}
        for k in data:
            if '归属于母公司所有者的净利润[' in k:
                d_profit[re.sub(r'\D', '', k)] = data[k]
        res = request_iwencai_robot_api(self.code + ' 2014到2018年年度分红总额')
        print(res)
        content = res['data']['answer'][0]['txt'][0]['content']
        json_data = json.loads(content)
        dividend = json_data['components'][0]['data']
        d_dividend = {}
        for d in dividend:
            d_dividend[d['时间区间']] = d['年度分红总额']
        # 求除数
        for k in d_profit:
            self.dividend_rate.append((k, d_dividend.get(k, 0) / d_profit[k] * 100))

    def get_rights_issue(self):
        """
        查询配股和供股记录
        """
        res = request_iwencai_robot_api(self.code + '供股合股记录')
        txt = res['data']['answer'][0]['txt'][0]
        self.rights_issue = {'has': '没有找到符合该条件的结果' != txt['content'], 'content': txt['content']}

    def get_stock_detail(self):
        """
        调用雪球网获取股票详情，主要是股息，每股收益，当前价格来计算好价格
        """
        url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol={}&extend=detail'.format(self.code)
        r = requests.get(url, headers=xueqiu_headers)
        res = r.json()
        detail = res['data']['quote']
        self.current_price = detail['current']
        self.eps = detail['eps']
        self.pe_ttm = detail['pe_ttm']
        self.dividend = detail['dividend']


class SeaSelect:
    """
    海选股票
    """

    condition = ''

    def __init__(self, condition):
        self.condition = condition

    def select(self):
        res = request_iwencai_stock_pick(self.condition)
        data = res['data']['data']
        # return [Stock(data[0])]
        return [Stock(d) for d in data]


def print_stock(base_stocks):
    print('海选出的股票有：')
    print('|股票|编码|ROE|')
    for stock in base_stocks:
        print('|{}|{}|'.format(stock.name, stock.code), end=' ')
        for roe in stock.roe:
            print('[{}]{:.2f},'.format(roe[0], float(roe[1])), end=' ')
        print('|')


def select_carefully(stock):
    """
    精挑细选5个条件：
    1、连续 5 年的 ROE 中,平均值或最近 1 年的数值低于 20%的,淘汰掉
    2、连续 5 年的平均净利润现金含量低于 100%的,淘汰掉
    3、连续 5 年的毛利率中,平均值或最近 1 年的数值低于 40%的,淘汰掉
    4、连续 5 年的资产负债率中,平均值或最近 1 年的数值大于 60%的,淘汰掉
    5、连续 5 年的派息比率中,有 1 年或 1 年以上小于 30%的,淘汰掉
    6、自上市以来,有过合股、供股、配股记录的,淘汰掉
    :return true/false 是否是好股票
    """
    try:
        check_avg(stock.name, stock.roe, 19, 'ROE')
        check_avg(stock.name, stock.profit_cash_ratio, 100, '净利润现金含量', False)
        check_avg(stock.name, stock.gross_profit, 40, '毛利率')
        check_avg(stock.name, stock.asset_liability, 60, '资产负债率', True)
        check_avg(stock.name, stock.dividend_rate, 29, '派息比率')
        if stock.rights_issue['has']:
            raise Exception('有过合股、供股、配股记录：{}'.format(stock.rights_issue['content']))
        return True
    except Exception as e:
        print('发现异常[{}]，淘汰【{}】'.format(e, stock.name))
        return False


def check_avg(name, arr, value, tag, should_small=False, check_first=True):
    """
    验证不合格抛异常
    :param name:
    :param should_small: 默认小于value
    :param tag: 说明
    :param value: 目标值
    :param arr: roe,毛利率等数组
    :param check_first: 是否检查第一年
    :return: True
    """
    ok = True
    msg = ''
    v_last_year = float(arr[len(arr) - 1][1])
    if check_first and (
            (should_small and v_last_year >= value) or (not should_small and v_last_year < value)):
        msg = '最近一年的[{}]值={:.2f}%不符合要求值：{:.2f} '.format(tag, v_last_year, value)
        ok = False
    v_sum = 0
    print('{}的{}:'.format(name, tag), end=' ')
    for a in arr:
        print('({}/{:.2f})'.format(a[0], float(a[1])), end=', ')
        v_sum += float(a[1])
    v_avg = v_sum / len(arr)
    tmp = '连续{}年的[{}]平均值={:.2f}'.format(len(arr), tag, v_avg)
    print('{}:{},要求值为：{}'.format(name, tmp, value))
    if (should_small and v_avg >= value) or (not should_small and v_avg < value):
        msg += ' {}，不符合要求值：{:.2f}'.format(tmp, value)
        ok = False
    if not ok:
        raise Exception(msg)


def cal_good_price(stock, max_10_year_bond_rate):
    """
    1.股息率
    TTM股息/好价格 = 中国10年期国债收益率 和 美国10年国债收益率 取大的
    2.市盈率
    每股收益×15=好价格
    3.求1和2个最小值
    :param max_10_year_bond_rate:
    :param stock:
    :return: 好价格
    """
    # 1.
    gp1 = stock.dividend / max_10_year_bond_rate
    # 2.
    gp2 = stock.eps * 15
    # 3.min
    print('{}:根据股息率计算的好价格为（TTM股息/国债收益率）：{:.2f}/{:.4f}={:.2f},'
          '根据市盈率计算的好价格为（每股收益×15）：{:.2f}×15={:.2f},'
          '取最小值为：{:.2f}'.format(stock.name, stock.dividend, max_10_year_bond_rate, gp1,
                                stock.eps, gp2, min(gp1, gp2)))


def get_max_10_year_bond_rate():
    # TODO
    c_10 = 0.027376
    a_10 = 0.0074
    print('中国和美国十年期国债收益率分别为：{:.4f},{:.4f},取较大者：{:.4f}'.format(c_10, a_10, max(c_10, a_10)))
    return max(c_10, a_10)


def main_run():
    con = '2014年到2018年净资产收益率ROE大于15%，2014年到2018年净利润现金含量大于80%，' \
          '2014年到2018年毛利率大于30%，上市大于三年,2014到2018年资产负债率小于70%'
    ss = SeaSelect(con)
    base_stocks = ss.select()

    # TODO debug
    # base_stocks = base_stocks[:1]

    # print base_stocks
    print_stock(base_stocks)

    # for each stock, select carefully
    good_stocks = [stock for stock in base_stocks if select_carefully(stock)]

    # 获取中国美国的最大10年期国债收益率
    max_10_year_bond_rate = get_max_10_year_bond_rate()

    print('精挑细选共选出{}家公司,计算其好价格：'.format(len(good_stocks)))
    # for each good stock, calculate its good price
    for stock in good_stocks:
        cal_good_price(stock, max_10_year_bond_rate)


if __name__ == '__main__':
    main_run()
