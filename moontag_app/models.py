from django.db import models
from django.utils.html import mark_safe # send safely into django data and can put photos to the App in the admin panel
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100)
    img = models.ImageField(upload_to='media/category_images')

    class Meta:
        verbose_name_plural = '1. Categories'

    def image_tag(self):
        return mark_safe('<img src="%s" width="60" height="60" />' % (self.img.url))

    def __str__(self):
        return self.title


class Brand(models.Model):
    title = models.CharField(max_length=100)
    img = models.ImageField(upload_to='media/brand_images')

    class Meta:
        verbose_name_plural = '2. Brands'

    def __str__(self):
        return self.title


class Color(models.Model):
    title = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = '3. Colors'

    def color_tag(self):
        return mark_safe('<div style="width:30px; height:30px; background-color:%s"></div>' % (self.color_code))

    def __str__(self):
        return self.title


class Size(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = '4. Sizes'

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=400)
    detail = models.TextField()
    specs = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    color = models.ForeignKey(Color,on_delete=models.CASCADE)
    size = models.ForeignKey(Size,on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = '5. Products'

    def __str__(self):
        return self.title

class Banner(models.Model):
    img = models.ImageField(upload_to='media/banner_images')
    text = models.CharField(max_length=300)

    def image_tag(self):
        return mark_safe('<img src="%s" width="90"/>' % (self.img.url))

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = '6. Banners'

class ProductAttribute(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    color = models.ForeignKey(Color,on_delete=models.CASCADE)
    size = models.ForeignKey(Size,on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    img = models.ImageField(upload_to="media/product_images",null=True)
    
    class Meta:
        verbose_name_plural = '7. Product Attribute'

    def __str__ (self):
        return self.product.title 

    def image_tag(self):
        return mark_safe('<img src="%s" width="60" height="60" />' % (self.img.url))


class CartOrder(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_amt = models.FloatField()
    paid_status = models.BooleanField(default=False)
    order_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '8. Cart order'

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder,on_delete=models.CASCADE)
    in_num = models.CharField(max_length=150)
    item = models.CharField(max_length=150)
    img = models.CharField(max_length=200)
    qty = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField() # save according the price and qty

    class Meta:
        verbose_name_plural = '9. Cart order items'

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="60" height="60" />' % (self.img))


RATING = (
    (1,'1'),
    (2,'2'),
    (3,'3'),
    (4,'4'),
    (5,'5'),
)

class ProductReview(models.Model):
    user = models.CharField(max_length=100,editable=False)
    product = models.CharField(max_length=100,editable=False)
    review_text = models.TextField()
    review_rating = models.CharField(choices=RATING, max_length=150)
    
    class Meta:
        verbose_name_plural = 'A10. Product Review'


class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'A11. Wishlist'

class Vendors(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    store_img = models.ImageField(upload_to="media/store_images",null=True)
    business_email = models.EmailField(max_length=254)
    pay_pal = models.EmailField(max_length=254)

    class Meta:
        verbose_name_plural = 'A12. Vendors'

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="60" height="60" />' % (self.img))


class VendorAddProduct(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'A13. Vendors Products'


class Todo(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    todo = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'A14. Todo'


class Withraw(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.FloatField()

    class Meta:
        verbose_name_plural = 'A15. Withraw'

