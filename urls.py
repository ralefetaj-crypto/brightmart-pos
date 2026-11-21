from django.urls import path
from . import views

urlpatterns = [
path("", views.dashboard, name="dashboard"),
path("products/", views.product_list, name="product_list"),
path("products/add/", views.product_create_or_edit, name="product_add"),
path("products/<int:pk>/edit/", views.product_create_or_edit, name="product_edit"),
path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
path("suppliers/", views.supplier_list, name="supplier_list"),
path("sales/new/", views.record_sale, name="record_sale"),
path("reports/sales/", views.sales_report, 

name="sales_report"),
]
