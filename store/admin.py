from django.contrib import admin
from .models import Product, Cart, CartItem, UserProfile, Transaction, UserLibrary, Wishlist, Review, StoreBanner

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(UserProfile)
admin.site.register(Transaction)

class UserLibraryAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('products',)

admin.site.register(UserLibrary, UserLibraryAdmin)

admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(StoreBanner)