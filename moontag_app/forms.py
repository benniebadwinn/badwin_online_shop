from django import forms
from moontag_app.models import Product, ProductAttribute



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title','slug','detail','specs','category','brand','color','size','status','is_featured']


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['product','color','size','price','img']

