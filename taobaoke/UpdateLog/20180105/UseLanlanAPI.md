2018.01.05
改动fetch_lanlan,(目前在新文件fetch_lanlan_modify.py中)
使用懒懒的api，已经全部完成并且测试通过。

## todo:
搜索的接口暂不改吧， 目前dianjin的接口稳定的一批

Done
淘口令的获取方式更新, update_token方法弃用 ** 测试通过 **
item_id在爬取商品时即获取，删除Product.save()方法，保存时直接调用entry的save **测试通过**
分类及详情在懒懒api直接获取，不再需要通过@receive实现的create_detail_and_cate **测试通过**
删除productdetail模型中的cate, 需要migrate **测试通过**
商品新增字段分类，不再使用ProductCategory模型  ### 需要migrate **测试通过**
 修改获取推单的详情的视图 **测试通过**
 修改选择分类和按所选分类进行商品筛选的视图 **测试通过**
原来的cate数据迁移- - **测试通过**


部署过程：

代码合并
停机
migrate
运行cate_migrate.py
完成后须update一下supervisor
