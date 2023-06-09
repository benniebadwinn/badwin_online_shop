from django.contrib import admin
from moontag_app.models import Category,Color,Size,Brand,Product,ProductAttribute,Banner,CartOrder,CartOrderItems,ProductReview,Wishlist,Vendors,VendorAddProduct,Todo,Withraw


# Register your models here.


class BannerAdmin(admin.ModelAdmin):
    list_display = ('text','image_tag')
admin.site.register(Banner, BannerAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','image_tag')
admin.site.register(Category, CategoryAdmin)

class ColorAdmin(admin.ModelAdmin):
    list_display = ('title','color_tag')
admin.site.register(Color,ColorAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','title','category','brand','color','size','status','is_featured') # its a tuple but i will remember the name list better
    list_editable = ('status','is_featured')
admin.site.register(Product, ProductAdmin)

class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id','image_tag','product','price','color','size')
admin.site.register(ProductAttribute, ProductAttributeAdmin)

class CartOrderAdmin(admin.ModelAdmin):
    list_display = ('user','total_amt','paid_status','order_dt')
admin.site.register(CartOrder, CartOrderAdmin)

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ('in_num','item','image_tag','qty','price','total')
admin.site.register(CartOrderItems, CartOrderItemsAdmin)

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user','product','review_text','review_rating')
admin.site.register(ProductReview, ProductReviewAdmin)

class VendorsAdmin(admin.ModelAdmin):
    list_display = ('user','store_name','company_name','business_email')
admin.site.register(Vendors, VendorsAdmin)

class WithrawAdmin(admin.ModelAdmin):
    list_display = ('user','amount')
admin.site.register(Withraw, WithrawAdmin)

class TodoAdmin(admin.ModelAdmin):
    list_display = ('user','todo')
admin.site.register(Todo, TodoAdmin)

class VendorAddProductAdmin(admin.ModelAdmin):
    list_display = ('user','product')
admin.site.register(VendorAddProduct, VendorAddProductAdmin)

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user','product')
admin.site.register(Wishlist, WishlistAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(Brand, BrandAdmin)

class SizeAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(Size, SizeAdmin)