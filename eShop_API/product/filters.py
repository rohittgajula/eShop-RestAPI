from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):

    keyword = filters.CharFilter(field_name=('name'), lookup_expr="icontains")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")     # gte -> greater than equal value
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")     # lte -> lessthan than equal value

    class Meta:
        model = Product
        fields = ('category', 'brand', 'keyword', 'min_price', 'max_price')

