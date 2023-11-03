
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('product.urls')),
    path('api/', include('account.urls')),
    path('api/', include('order.urls')),

    path('api/token/', TokenObtainPairView.as_view()),
]

handler404 = 'utils.errors_views.handler404'
handler500 = 'utils.errors_views.handler500'

