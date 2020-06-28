import json
import logging


def get_logger(name):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('jimo_' + name)
    return logger


log = get_logger('info.log')


def load_json_item(code, name):
    item = {}
    with open('data/{}_{}.json'.format(name, code), 'r') as f:
        one_list = json.load(f)
    for d in one_list:
        # 取出年份为key
        item[int(d['report_name'][:4])] = d
    return item


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
        self.end_year = end_year
        self.file_name = file_name
        self.data = self.init_data()
        print(self.data)
        # self.wb = xlwt.Workbook(encoding='utf-8')

    def init_data(self):
        data = {}
        for code in self.codes:
            one = {'asset': load_json_item(code, 'asset'),
                   'cash': load_json_item(code, 'cash'),
                   'profit': load_json_item(code, 'profit')}
            data[code] = one
        return data

    def execute_all(self):
        # TODO 23 step
        self.step_01()
        self.wb.save('{}.xlsx'.format(self.file_name))

    def step_01(self):
        log.info('开始总资产分析...')
        sheet = self.wb.add_sheet('总资产', cell_overwrite_ok=True)


if __name__ == '__main__':
    g = GenerateReport(['SZ000895'], 2015, 2019)
