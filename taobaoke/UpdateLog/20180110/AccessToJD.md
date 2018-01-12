## 2018.01.10 引入京东商品

新增：
    京东商品模型: broadcast.entry_models.JDProduct
        对应的爬取商品脚本: scripts.goods.fetch_hjk.py（运行间隔为4小时）

    京东推广位模型（极简）: broadcast.user_models.JDAdzone
        对应的爬取推广位脚本: scripts.hjk.fetch_jdpid.py

    top_settings.py中增加京东接口所用的apikey和unionid.

    settings.py中增加一个logger - fetch_hjk


改动:
    Entry模型添加一个property: Entry.p， 可以获取其对应的Product或JDProduct实例
    PushProduct接口，进一步拆分，选取商品使用单独的方法choose_a_product, 使用Entry模型筛选，并用p属性获取商品。
        另外， 获取pid-生成图片的过程中，加入对tkuser是否拥有Adzone及JDAdzone的判断，若没有则分配。

    ProductDetail_接口，兼容了京东的商品。 明天测试

    兼容京东订单， Order模型加入成吨null=True
    对订单加入user_id的过程分别加入pub_alimama_data和update_jd_orders, 原Order.save()中的删掉
    在main()方法一开始加入update_jd_orders方法，更新京东订单。


部署流程：
    1.migrate
    2.一次运行fetch_jdpid.py
    3. supervisor新建一条任务，运行fetch_hjk.py
    4.  supervisor需要update(main文件有更新)

    **需与小程序一起部署，否则可能有问题**

目前搜索没有支持京东，所以SearchDetail暂时不用处理。



## todo: 订单更新部分的处理。使用好京客接口。