from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('home/', views.product_list, name='product-list'),
    path('logout/', views.logout_user, name='logout'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.view_profile, name='view_profile'),
    path('wallet/topup/', views.top_up_wallet, name='top_up_wallet'),
    path('repository/', views.repository, name='repository'),
    path('refund/<int:transaction_id>', views.refund_game, name='refund_game'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]