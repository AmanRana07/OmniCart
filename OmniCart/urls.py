"""
URL configuration for OmniCart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from OmniApp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("cart/", cart_view, name="cart"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("adminpanel/<uuid:customer_id>", AdminPanelView.as_view(), name="admin_panel"),
    path("add_product/", add_product, name="add_product"),
    path("product-list/", product_list, name="product_list"),
    path("product/edit/<uuid:product_id>/", product_edit, name="product_edit"),
    path("product/delete/<uuid:product_id>/", product_delete, name="product_delete"),
    path("shop/", shop, name="shop"),
    path("shops/", shops, name="shops"),
    path("product/<uuid:product_id>/", product_detail, name="product_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
