import requests


class LoadReport(object):

    def __init__(self, code):
        self.code = code

    def req_data(self):
        """
        请求最近6年年报数据
        :return: 结构如下：{
        currency: "CNY"
        currency_name: "人民币"
        last_report_name: "2020一季报",
        list: [{},{},{},{},{},{}]
        org_type: 1
        quote_name: "双汇发展"
        }
        list里就是具体项目数据，查看文件
        """
        url = 'https://stock.xueqiu.com/v5/stock/finance/cn/income.json?symbol={}&type=Q4&is_detail=true&count=6' \
              '&timestamp='.format(self.code)
        header = self.get_header()
        res = requests.get(url, headers=header)
        return res.json()['data']

    def write_excel(self):
        pass

    @staticmethod
    def get_header():
        header = {'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip, deflate, br',
                  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8', 'Connection': 'keep-alive',
                  'Host': 'stock.xueqiu.com', 'Origin': 'https://xueqiu.com',
                  'Referer': 'https://xueqiu.com/snowman/S/SZ000895/detail', 'Sec-Fetch-Dest': 'empty',
                  'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/83.0.4103.61 Safari/537.36',
                  'Cookie': 'device_id=24700f9f1986800ab4fcc880530dd0ed; s=cs1cqgondz; xq_a_token=ea139be840cf88ff8c30e6943cf26aba8ad77358; xqat=ea139be840cf88ff8c30e6943cf26aba8ad77358; xq_r_token=863970f9d67d944596be27965d13c6929b5264fe; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTU5NDAwMjgwOCwiY3RtIjoxNTkxNTMxODQyMjM1LCJjaWQiOiJkOWQwbjRBWnVwIn0.o189WRRzRJQDSnP8USNyktdNaz8yhPjm9rfvZtXHymOz8IoQm0EPetmfo4Psn7L3x5Zqroo-_p8sITOiuqvi32iIuIUkR6ZpitpaBhWywJPdV836iiIrlJ3lThIYlqrtkzgqyhhq5A6t6XYszGezYjrFdpwNgjPbrnD3OdvVb5zHTIwfR9O80_8HxM60NRygoBgam_UZqhGurrN8nzEO9nDyYGPnAHnxDRAz4kgbZWGfklLWFijqLLQaFvnN_0jSMQhO_J0QNpr4SJ2O6kkCuyanHHR28xotFJs-r_awAkNEdzkvdOu-5HdmzSwqDjLQSBlQvwE3jgBCAgCUU6BSNA; u=941591531846409; Hm_lvt_1db88642e346389874251b5a1eded6e3=1591531849; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1592123351'
                  }
        return header


if __name__ == '__main__':
    r = LoadReport('SZ000895')
    j = r.req_data()['list'][0]
    for k in sorted(j.keys()):
        print('"{}":"",'.format(k))
