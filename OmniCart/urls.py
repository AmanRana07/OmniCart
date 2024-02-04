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
    path("cart/", view_cart, name="cart"),
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
    path("add_to_cart/<uuid:product_id>/", add_to_cart, name="add_to_cart"),
    path(
        "update-cart-quantity/<int:item_id>/<int:new_quantity>/",
        update_cart_quantity,
        name="update_cart_quantity",
    ),
    path("remove-cart-item/<int:item_id>/", remove_cart_item, name="remove_cart_item"),
    path("checkout/", checkout, name="checkout"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
    path("orders/", order_list, name="order_list"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
    path(
        "orders/<int:order_id>/update-status/",
        update_order_status,
        name="update_order_status",
    ),
    path("get-categories/", get_categories, name="get_categories"),
    path("category/<int:category_id>/", category_view, name="category"),
    path("tags/<int:tag_id>/", tag_view, name="tag"),
    path("get-tags/", get_tag, name="get_tag"),
    path("search/", search_view, name="search_view"),
    path("profile/", my_account, name="my_account"),
    path('privacy-policy/', privacy, name="privacy"),
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
