## 2018.01.04: 手动推送商品提供队列功能，

### 新增
    队列在entry_utils.py中增加HandlePushFIFO类。 **测试通过**
    taobaoke_views.py 中增加send_msg方法, 参数为username和msg_list， 通过此方法调用04服务器上的接口发送消息。 **测试通过**
    taobaoke_views.py 中增加global_push_from_fifo方法， 无参数， 通过此方法从所有在线用户的队列中取出消息并发送（受handle_pushtime限制）**测试通过**
    send_request.py 中增加调用global_push_from_fifo方法， 每分钟尝试取出消息（22：00-07：00时间隔为20分钟）**测试通过**

### 更改
    taobaoke_views.py
    更改PushCertainProduct视图，参数为username和item_id, 将商品消息组成列表后推入fifo, 且此时不受handle_pushtime限制 **测试通过**
    get_handle_pushtime方法中增加一个返回数据， 是目前队列中带推送的商品数量 **测试通过**
