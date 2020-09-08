from MongoClient import Mongo
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.charts import PictorialBar
from pyecharts.globals import SymbolType
from pyecharts.options import ComponentTitleOpts
from pyecharts.globals import ThemeType
from pyecharts.charts import Map
import threading
from pyecharts.charts import Bar
from word_cloud import Cloud
import re


class Analysis:
    def __init__(self):
        self.collection = Mongo().Collection

    def price_distribution(self):
        print('生成价格频率分布图ing...')
        range_lst = []
        rate_lst = []
        num = 2000
        while num < 20000:
            rate = self.collection.find({'商品价格': {'$gte': num, '$lt': num + 2000}}).count()
            range_lst.append('—'.join([re.sub('000', '', str(i)) + 'K' for i in [num, num + 2000]]))
            rate_lst.append(rate)
            num += 2000

        c = (
            Bar()
            .add_xaxis(range_lst)
            .add_yaxis("频数", rate_lst)
            .set_global_opts(title_opts=opts.TitleOpts(title="价格频率分布直方图"))
            .render("价格频率分布图.html")
        )
        print('生成完成')

        return c

    def shop_map(self):
        print('生成销售分布地图ing...')
        place_dict = {}
        for item in self.collection.find({}, {'店铺地址': 1, '_id': 0}):
            addr = item['店铺地址'].split(' ')[0]
            place_dict[addr] = place_dict.setdefault(addr, 0) + 1

        data_lst = [[key, value] for key, value in place_dict.items()]

        c = (
            Map()
            .add('数据源', data_lst, 'china')
            .set_global_opts(
                title_opts=opts.TitleOpts(title='销售地分布情况'),
                visualmap_opts=opts.VisualMapOpts(max_=700),
            )
        ).render('销售分布地图.html')
        print('生成完成')

        return c

    def sales_top(self):
        print('正在生成店铺商品销量Top10...')
        sales_lst = []
        shop_lst = []
        info_lst = self.collection.find({}, {'店铺名称': 1, '商品销量': 1}).sort('商品销量', -1).limit(10)
        for item in info_lst:
            sales_lst.append(item['商品销量'])
            shop_lst.append(item['店铺名称'])

        c = (
            Bar({"theme": ThemeType.MACARONS})
            .add_xaxis(shop_lst)
            .add_yaxis('销量', sales_lst)
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
                title_opts={'text': '店铺商品销量Top10'}
            )
            .render("店铺商品销量Top10.html")
        )
        print('生成完成')

        return c

    def table(self):
        print('正在生成表格...')
        table = Table()

        headers = ['商品详情', '商品价格', '商品销量', '店铺名称', '店铺地址', '商品图片', '商品主页']
        rows = [list(item.values()) for item in self.collection.find({}, {'_id': 0})]
        table.add(headers, rows)
        table.set_global_opts(
            title_opts=ComponentTitleOpts(title="数据源表格汇总")
        )
        table.render("表格汇总.html")
        print('生成完成')

    def word_cloud(self):
        Cloud().run()
        print('词云生成完成')

    def place_top(self):
        print('正在生成销售地Top10...')
        group_count = self.collection.aggregate([{'$group': {'_id': '$店铺地址', 'count': {'$sum': 1}}}])

        addr = []
        count = []
        sorted_list = sorted([list(item.values()) for item in group_count], key=lambda x: x[-1], reverse=True)
        for item in sorted_list[:10][::-1]:
            addr.append(item[0])
            count.append(item[1])

        c = (
            PictorialBar()
            .add_xaxis(addr)
            .add_yaxis(
                '',
                count,
                label_opts=opts.LabelOpts(is_show=False),
                symbol_size=16,
                symbol_repeat='fixed',
                symbol_offset=[0, 0],
                is_symbol_clip=True,
                symbol=SymbolType.ROUND_RECT,
            )
            .reversal_axis()
            .set_global_opts(
                title_opts=opts.TitleOpts(title='销售地Top10'),
                xaxis_opts=opts.AxisOpts(is_show=False),
                yaxis_opts=opts.AxisOpts(
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(opacity=0)
                    ),
                ),
            )
            .render("销售地Top10.html")
        )
        print('生成完成')

        return c


if __name__ == '__main__':
    start = Analysis()
    tasks = [
        start.price_distribution,
        start.shop_map,
        start.word_cloud,
        start.place_top,
        start.sales_top,
        start.table
    ]
    for task in tasks:
        t = threading.Thread(target=task)
        t.start()
