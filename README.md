# 二手商品交易平台——GoodiesMoreMarket

该项目实现了一个二手商品交易平台，用户可以在本地使用python运行该平台，并且可以通过注册成为买家或者卖家，并在平台上完成发布商品、购买商品等操作。

## 环境

- Windows 10

- python3

- pymysql 0.9.3

- flask 1.1.1

- flask-login 0.4.1

  以上环境可以在windows的命令行界面通过pip install命令安装。如果事先没有安装pip，应该在安装pip后配置上述环境。

## 如何运行

进入项目文件夹，在命令行中输入python myflask.py即可运行平台，然后在浏览器中输入http://localhost:5000， 出现以下页面，说明成功。

![image](https://github.com/Howllow/Second-Hand-Platform/blob/master/1576770000960.png)

## 注册账号

点击“click here to register”按钮，即可进入注册页面。根据提示输入信息即可完成注册。

## 如何使用

如果注册成为卖家，需要等待管理员同意后方可登录进入卖家页面执行相关操作；

如果注册成为买家，则可以直接登录进入系统。

## 如何登出系统

点击右上角姓名，点击logout按钮即可登出。

## 结束程序

在打开的命令行中Ctrl+C即可关闭平台。

## 项目文件夹中代码功能说明

* 项目根目录中
  * myflask.py可以运行平台，并处理url跳转等请求
  * user.py定义用户类
* templates文件夹中为各个页面的html格式
* static文件夹中存放模板的图片
* db文件夹中
  * createxml.py可以动态生成商品的xml文件
  * config.py存放连接数据库的配置文件
  * dbgmm.py连接数据库，并进行一些数据库中的sql查询、更改等操作
  * test.py测试数据库连接
  * utils.py提供检查用户存在性等功能

