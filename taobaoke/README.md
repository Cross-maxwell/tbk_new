# Overview
The whole story has three parts:  
1. Weixin Bot. The bot runs on cloud and provides API for 3rd-party apps.
2. Product DB and crawler. We can crawl products from various sources.
3. Product picker. Not included in this system. Should be included in the future.

# Weixin bot
Refer to qunzhu.me

# Product DB and crawler
See `broadcast` app in django project.  
Crawler scripts are in /scripts/goods folder.  

# Walk through
1. Run django project for product insertion.  
`python manage.py runserver 0.0.0.0:8000`  
2. Run spider to fetch products.  
`scrapy runspider scripts/goods/fetch_dtk.py`  
3. Start spamming (it sucks...)  
`watch --interval 120 python manage.py push`

# 成单数据推送
```
推送逻辑：
5mins根据cookie文件，推送一次数据。
若新cookie文件已经失效，则不会再推送，直到下次监测cookie文件是否更改，若有更改，则尝试新cookie文件.
如果生效。则会继续5分钟推送。
```
