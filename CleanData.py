from MongoClient import Mongo


class Clean:
    def __init__(self):
        self.collection = Mongo().Collection

    def data_clean(self):
        for detail in self.collection.distinct('商品图片'):
            num = self.collection.count({"商品图片": detail})
            print(num)
            for i in range(1, num):
                print('删除 %s %d 次 ' % (detail, i))
                self.collection.remove({"商品图片": detail}, 0)
        print('数据清洗成功')


if __name__ == '__main__':
    Clean().data_clean()
