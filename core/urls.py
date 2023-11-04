from django.urls import path
from . import views

urlpatterns = [
    path('/add_polygon/', views.add_polygon, name='add_polygon_api'),
    path('/calculate_ndvi/<int:polygon_id>/', views.calculate_ndvi, name='calculate_ndvi_api'),
]
