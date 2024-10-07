from django.urls import path, include
from rest_framework import routers
from .views import BooksViewSet


router = routers.DefaultRouter()
router.register('', BooksViewSet)

urlpatterns = [
    path('purchase-book/', BooksViewSet.as_view({'post': 'purchase_book'})),
    path('', include(router.urls)),
]