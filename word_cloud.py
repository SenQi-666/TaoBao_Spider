import jieba
import re
from MongoClient import Mongo
import collections
from pyecharts import options as opts
from pyecharts.charts import WordCloud


class Cloud:
    def __init__(self):
        self.collections = Mongo().Collection

    def jieba_cut(self, detail_lst):
        print('正在分词中，请稍后......')
        jieba_lst = []
        stopwords = self.stop_words_list()
        for detail in detail_lst:
            strings = re.sub(r'\W|\s', '', detail.strip())
            cut_list = jieba.lcut(strings, cut_all=False)
            for word in cut_list:
                if word not in stopwords:
                    jieba_lst.append(word)
        print('分词完成！')
        return jieba_lst

    @staticmethod
    def stop_words_list():
        with open('stop_words.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    @staticmethod
    def counter(jieba_lst):
        word_counts = collections.Counter(jieba_lst)
        words = [(key, value) for key, value in word_counts.items()]
        return words

    @staticmethod
    def echarts_wordcloud(words):
        c = (
            WordCloud()
            .add(
                "",
                words,
                word_size_range=[50, 100],
                textstyle_opts=opts.TextStyleOpts(font_family="cursive"),
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="商品词云统计"))
            .render("商品词云.html")
        )
        return c

    def run(self):
        detail_list = [item['商品详情'] for item in self.collections.find({}, {'商品详情': 1, '_id': 0})]
        jieba_list = self.jieba_cut(detail_list)
        self.echarts_wordcloud(self.counter(jieba_list))


if __name__ == '__main__':
    Cloud().run()
