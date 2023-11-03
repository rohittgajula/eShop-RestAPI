from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from django.db.models import Avg        # helps to calculate averagess

from .filters import ProductFilter
from .models import Product, ProductImages, Review
from .serializers import ProductSerializer, ProductImagesSerializer

@api_view(['GET'])
def get_products(request):
    filterset = ProductFilter(request.GET, queryset=Product.objects.all().order_by('id'))

    # to show no. of items.
    count = filterset.qs.count()

    # pagination
    resPerPage = 3
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage
    queryset = paginator.paginate_queryset(filterset.qs, request)

    #products = Product.objects.all()
    # serializer = ProductSerializer(filterset.qs, many=True)
    serializer = ProductSerializer(queryset, many=True)
    return Response({
        'count':count,
        'resPerPage':resPerPage,
        'products':serializer.data
    })

@api_view(['GET'])
def get_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response({
        'product':serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_product(request):
    data = request.data
    serilaizer = ProductSerializer(data=data)
    if serilaizer.is_valid():
        product = Product.objects.create(**data, user=request.user)     # user field automatically saves logined user.
        res = ProductSerializer(product, many=False)
        return Response({
            'product':res.data
        })
    return Response(serilaizer.errors)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # checking if created user = updateing user
    if product.user != request.user:
        return Response({
            'error':'You cannot update this product.'
        }, status.HTTP_401_UNAUTHORIZED)

    product.name = request.data['name']
    product.description = request.data['description']
    product.price = request.data['price']
    product.category = request.data['category']
    product.brand = request.data['brand']
    product.ratings = request.data['ratings']
    product.stock = request.data['stock']

    product.save()

    serializer = ProductSerializer(product, many=False)
    return Response({
        'product':serializer.data
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # checking if created user = updateing user
    if product.user != request.user:
        return Response({
            'error':'You cannot delete this product'
        })

    # this filters image using id/pk from 1st line.
    args = { "product":pk }
    images = ProductImages.objects.filter(**args)
    for i in images:
        i.delete()

    product.delete()
    return Response({
        'message':'Product is deleated.'
    }, status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_product_images(request):

    data = request.data
    files = request.FILES.getlist('images')

    images = []
    for f in files:
        image = ProductImages.objects.create(product=Product(data['product']), image = f )
        images.append(image)
    serializer = ProductImagesSerializer(images, many=True)

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)
    data = request.data

    review = product.reviews.filter(user=user)      # .reviews is the related name given to review.product in model

    if data['rating'] <= 0 or data['rating'] > 5:
        return Response({ 'error': 'Please select rating between 1-5' }, status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = { 'rating': data['rating'], 'comment': data['comment'] }
        review.update(**new_review)
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()
        return Response({ 'detail': 'Review Updated' })
    else:
        Review.objects.create(
            user=user,
            product=product,
            rating = data['rating'],
            comment = data['comment']
        )
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
        product.ratings = rating['avg_ratings']
        product.save()
        return Response({ 'detail': 'Review Posted' })
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)

    review = product.reviews.filter(user=user)
    if review.exists():
        review.delete()

        # finding average rating 
        rating = product.reviews.aggregate(avg_ratings=Avg('rating'))

        # if average rating is none we are giving it none or it shows error.
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0

        product.ratings = rating['avg_ratings']     # save avg rating in the product
        product.save()
        return Response({'detail':'review deleated'})
    
    else:
        return Response({
            'error':'review not found',
        }, status.HTTP_404_NOT_FOUND)
    
