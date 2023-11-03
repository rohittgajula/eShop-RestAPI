from rest_framework import serializers

from .models import Product, ProductImages, Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):

    images = ProductImagesSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)   # method is taken from function (get_reviews)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'ratings', 'brand', 'category', 'stock', 'user', 'reviews', 'images')

        # when name & description cannot be blank or empty
        extra_kwargs = {
            "name": {"required":True, 'allow_blank':False},
            "description": {"required":True, 'allow_blank':False},
            "brand": {"required":True, 'allow_blank':False},
            "category": {"required":True, 'allow_blank':False}
        }

    def get_reviews(self, obj):     # obj is the current product.
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data
    
