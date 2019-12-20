# -*- coding:UTF-8 -*-

from db.dbgmm import *
from db.config import *
from xml.dom.minidom import Document

def cxml(contents):
    dom = Document()
    root = dom.createElement('XML')
    dom.appendChild(root)

    goods = dom.createElement('Goods')
    root.appendChild(goods)

    print(contents[0])
    for content in contents:
        good = dom.createElement('Good')
        goods.appendChild(good)

        goodid = dom.createElement('GoodID')
        text = dom.createTextNode(str(content[0]))
        goodid.appendChild(text)
        good.appendChild(goodid)

        info = dom.createElement('Info')
        good.appendChild(info)

        basicinfo = dom.createElement('BasicInfo')
        info.appendChild(basicinfo)

        name = dom.createElement('Name')
        text = dom.createTextNode(str(content[8]))
        name.appendChild(text)
        basicinfo.appendChild(name)

        describe = dom.createElement('Describe')
        text = dom.createTextNode(str(content[3]))
        describe.appendChild(text)
        basicinfo.appendChild(describe)

        label = dom.createElement('Label')
        text = dom.createTextNode(str(content[2]))
        label.appendChild(text)
        basicinfo.appendChild(label)

        price = dom.createElement('Price')
        text = dom.createTextNode(str(content[5]))
        price.appendChild(text)
        basicinfo.appendChild(price)

        sellerid = dom.createElement('SellerID')
        text = dom.createTextNode(str(content[6]))
        sellerid.appendChild(text)
        basicinfo.appendChild(sellerid)

        comments = dom.createElement('Comments')
        info.appendChild(comments)

        comment = dom.createElement('Comment')
        text = dom.createTextNode(str(content[4]))
        comment.appendChild(text)
        comments.appendChild(comment)

    try:
        with open('gmm.xml', 'w', encoding='UTF-8') as fh:
            dom.writexml(fh, indent='', addindent='\t', newl='\n', encoding='UTF-8')
    except Exception as err:
        print('错误信息：{0}'.format(err))


def loadDb():
    db = pymysql.connect(**myconfig)
    cursorRead = db.cursor()
    cursorRead.execute("select * from gmm.goods")
    contents = cursorRead.fetchall()

    cxml(contents)
    db.close()


if __name__ == '__main__':
    loadDb()