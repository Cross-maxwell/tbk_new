import json

from django.views import View

from broadcast.models.entry_models import Product


class ProductView(View):
    def post(self, request):
        req_dict = json.loads(request.body)
        Product.objects.create(

        )