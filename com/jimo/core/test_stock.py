from unittest import TestCase
import json

import requests

xueqiu_headers = {
    'Host': 'stock.xueqiu.com',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36'
}


class TestStock(TestCase):

    def test_dict(self):
        s = '''
        {"components":[{"show_type":"table2","data":[{"年度分红总额":24078461100.43,"__code":"1928","股票简称":"金沙中国有限公司","时间区间":"20181231","股票代码":"1928"},{"年度分红总额":8080187091,"__code":"1928","股票简称":"金沙中国有限公司","时间区间":"20171231","股票代码":"1928"},{"年度分红总额":16063138558.55,"__code":"1928","股票简称":"金沙中国有限公司","时间区间":"20161231","股票代码":"1928"},{"年度分红总额":16058547231.55,"__code":"1928","股票简称":"金沙中国有限公司","时间区间":"20151231","股票代码":"1928"},{"年度分红总额":16055887587.05,"__code":"1928","股票简称":"金沙中国有限公司","时间区间":"20141231","股票代码":"1928"}],"puuid":16437,"config":{"other_info":{"perpage":6,"un_show_titles":{"index_name":[],"key":[]}},"title_data":{"透传指标":"年度分红总额"},"configuration_data":{"年度分红总额":{"unit":"港元","index":"年度分红总额","source":"new_parser","type":"DOUBLE"},"时间区间":{"unit":"","index":"时间区间","source":"","type":"date"}},"columns":[{"title_children":[],"data_index":["年度分红总额"],"width":0,"fixed":"left","title":["年度分红总额(港元)"]},{"title_children":[],"data_index":["时间区间"],"width":0,"fixed":"","title":["时间区间"]}],"direction":1},"analyze_data":{"total":5,"code_count":1},"uuid":"821aa2ba7f895b37f9771f478aaef7b8","cid":2298785}],"request_params":"business=1&business_cat=8&condition=%5B%7B%22chunkedResult%22%3A%22hk1928+2014%E5%88%B02018%E5%B9%B4%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%2C%22opName%22%3A%22and%22%2C%22opProperty%22%3A%22%22%2C%22sonSize%22%3A2%2C%22relatedSize%22%3A0%7D%2C%7B%22indexName%22%3A%22%E8%82%A1%E7%A5%A8%E4%BB%A3%E7%A0%81%22%2C%22indexProperties%22%3A%5B%22%E5%8C%85%E5%90%AB1928.HK%22%5D%2C%22source%22%3A%22new_parser%22%2C%22type%22%3A%22index%22%2C%22indexPropertiesMap%22%3A%7B%22%E5%8C%85%E5%90%AB%22%3A%221928.HK%22%7D%2C%22reportType%22%3A%22null%22%2C%22valueType%22%3A%22_%E6%B8%AF%E8%82%A1%E4%BB%A3%E7%A0%81%22%2C%22domain%22%3A%22abs_%E6%B8%AF%E8%82%A1%E9%A2%86%E5%9F%9F%22%2C%22uiText%22%3A%22%E8%82%A1%E7%A5%A8%E4%BB%A3%E7%A0%81%E6%98%AF1928.HK%22%2C%22sonSize%22%3A0%2C%22queryText%22%3A%22%E8%82%A1%E7%A5%A8%E4%BB%A3%E7%A0%81%E6%98%AF1928.HK%22%2C%22relatedSize%22%3A0%2C%22tag%22%3A%22%E8%82%A1%E7%A5%A8%E4%BB%A3%E7%A0%81%22%7D%2C%7B%22dateText%22%3A%222014%E5%B9%B4%E5%88%B02018%E5%B9%B4%22%2C%22indexName%22%3A%22%E6%B8%AF%E8%82%A1%40%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%2C%22indexProperties%22%3A%5B%22%E8%B5%B7%E5%A7%8B%E4%BA%A4%E6%98%93%E6%97%A5%E6%9C%9F+20141231%22%2C%22%E6%88%AA%E6%AD%A2%E4%BA%A4%E6%98%93%E6%97%A5%E6%9C%9F+20181231%22%5D%2C%22dateUnit%22%3A%22%E5%B9%B4%22%2C%22source%22%3A%22new_parser%22%2C%22type%22%3A%22index%22%2C%22indexPropertiesMap%22%3A%7B%22%E8%B5%B7%E5%A7%8B%E4%BA%A4%E6%98%93%E6%97%A5%E6%9C%9F%22%3A%2220141231%22%2C%22%E6%88%AA%E6%AD%A2%E4%BA%A4%E6%98%93%E6%97%A5%E6%9C%9F%22%3A%2220181231%22%7D%2C%22reportType%22%3A%22YEAR%22%2C%22dateType%22%3A%22%E6%8A%A5%E5%91%8A%E6%9C%9F%22%2C%22valueType%22%3A%22_%E6%B5%AE%E7%82%B9%E5%9E%8B%E6%95%B0%E5%80%BC%28%E5%85%83%7C%E6%B8%AF%E5%85%83%7C%E7%BE%8E%E5%85%83%7C%E8%8B%B1%E9%95%91%29%22%2C%22domain%22%3A%22abs_%E6%B8%AF%E8%82%A1%E9%A2%86%E5%9F%9F%22%2C%22uiText%22%3A%222014%E5%B9%B4%E5%88%B02018%E5%B9%B4%E7%9A%84%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%2C%22sonSize%22%3A0%2C%22queryText%22%3A%222014%E5%B9%B4%E5%88%B02018%E5%B9%B4%E7%9A%84%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%2C%22relatedSize%22%3A0%2C%22tag%22%3A%22%5B2014%E5%B9%B4%E5%88%B02018%E5%B9%B4%5D%E6%B8%AF%E8%82%A1%40%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%7D%5D&entity=%5B%7B%22type%22%3A%22code%22%2C%22word%22%3A%221928.HK%22%7D%5D&entity_map=&logid=054bc325020cec714fad150f417d2432&parse_res=%7B%22date_range%22%3A%5B%2220141231%22%2C%2220181231%22%5D%2C%22indexes%22%3A%5B%22%E8%82%A1%E7%A5%A8%E4%BB%A3%E7%A0%81%22%2C%22%E6%B8%AF%E8%82%A1%40%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%5D%2C%22domain%22%3A%22abs_%E6%B8%AF%E8%82%A1%E9%A2%86%E5%9F%9F%22%7D&query_type=hkstock&question_labels=%5B%22hk1928%22%2C%22%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D%22%5D&remove_switch=1&scene_val=2&sessionid=054bc325020cec714fad150f417d2432&source=Ths_iwencai_Xuangu&source_type=ths_company&tag=%E6%B8%AF%E8%82%A1_%E5%8D%95%E5%AF%B9%E8%B1%A1_%E5%8D%95%E6%8C%87%E6%A0%87&trace_debug=0&urp=&userid=Ths_iwencai_Xuangu_7b010e0adf28942dec9bc54745b94f90&uuid=16437&w=HK1928+2014%E5%88%B02018%E5%B9%B4%E5%B9%B4%E5%BA%A6%E5%88%86%E7%BA%A2%E6%80%BB%E9%A2%9D","global":{"requestTime":"2020-03-08 20:54:59","appModule":"Urp","appVersion":"V7","defaultCode":"1928","subjects":{"1928":{"rise_fall_rate":-3.48,"code":"1928","rise_fall":-1.25,"latest_price":34.7,"name":"金沙中国有限公司","hqcode":"HK1928","type":"hkstock","hqmarketcode":"177"}},"queryType":"hkstock"},"page":{"layout":{"layout_data":"","layout_mode":""},"cache_time":0,"ori_id":91612,"more":{"q":"HK1928 2014到2018年年度分红总额","codes":["1928.HK"],"isview":true,"display_board":false,"query_type":"hkstock"},"ori_scene":1,"uuids":["16437"]},"id":898759827}
        '''
        d = json.loads(s)
        print(d['components'][0]['data'])

    def test_xueqiu(self):
        d = 'xq_a_token=a664afb60c7036c7947578ac1a5860c4cfb6b3b5; ' \
            'xqat=a664afb60c7036c7947578ac1a5860c4cfb6b3b5; ' \
            'xq_r_token=01d9e7361ed17caf0fa5eff6465d1c90dbde9ae2; ' \
            'xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV' \
            '4cCI6MTU4NTM2MjYwNywiY3RtIjoxNTgzNjgyNjI5MDgyLCJjaWQiOiJkOWQwbjRBWnVwIn0.' \
            'nVT2cBhNGU9Hgs0JvEtoV8MagcYPVvaz6iXOF83DRC2AUW1vpsYqyuPsIUm7zNWN7N1kBrUr8NyC1OOT4kW' \
            '_cf8yZ1KewXyjVntWdAZBwRSXdDrIC6zjjP1N8ARQyFepsaz8dHJlpTSangUWdC3qrLW7qKQGYS0OUUvd' \
            'ILhnHGvOQrAmHeJWgN-8h4HT9BrpmlR9fErjIfn954_k7O-8yjiXTvTepMWt2MxtjREtiF6zMmZLppZpsBoGV5prsgbxaF' \
            '-OYY8LhMSzLSndfZ_LjM9YN7QrIBA4VX_xn3vUICrBm2YvMGoglMeo7T-cOvQGU-Atw-q0BA78hd0NkCoMFg; ' \
            'u=941583682640528; cookiesu=831583682643721; device_id=24700f9f1986800ab4fcc880530dd0ed;' \
            ' Hm_lvt_1db88642e346389874251b5a1eded6e3=1583682646; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1583682646'

        xueqiu_headers['Cookie'] = d
        url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol=01928&extend=detail'
        r = requests.get(url, headers=xueqiu_headers)
        print(r.json())
