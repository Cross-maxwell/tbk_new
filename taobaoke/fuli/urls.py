from django.conf.urls import url, include
from django.contrib import admin
from broadcast.views.entry_views import search_product, push_product, search_product_pad
from broadcast.views.user_views import update_adzone, get_adzone_info, get_tkuser_info, get_login_qrcode

user_urls = [
    url(r'^update-adzone/', update_adzone),
    url(r'^get-adzone-info/', get_adzone_info),
    url(r'^get-tkuser-info/', get_tkuser_info),
]

product_urls = [
    url(r'qrcode/', get_login_qrcode)
]

interact_urls = [
    url(r'search-product/', search_product),
    url(r'search-product-pad/', search_product_pad),
    url(r'push-product/', push_product),
]



urlpatterns = [
    url(r'product/', include(product_urls)),
    url(r'^user/', include(user_urls)),
    url(r'interact/', include(interact_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^ipad_weixin/', include('ipad_weixin.urls'))
]
