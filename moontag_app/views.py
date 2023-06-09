from django.shortcuts import redirect, render
from moontag_app.models import Product,Category,Brand,Banner,ProductAttribute,Color,Size,CartOrder,CartOrderItems,ProductReview,Wishlist,Vendors, VendorAddProduct,Todo,Withraw
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import moontag_project.settings as settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str 
from . tokens import generate_token
from django.contrib.auth.decorators import login_required 
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from moontag_app.forms import ProductForm, ProductAttributeForm
from django.db.models import Avg ,Sum
import json
from datetime import datetime



"""
Mail service login:
    link: https://mailtrap.io/signin
    email: bsbin6866@gmail.com
    password: Beny132001
    in the mailtrap website go to my inbox and than you will se the messeges to the email *enter to mailtrap after you registred to moontag website*

Superuser: * לא חייב להשתמש ביוזר הזה רק אם תרצה לבצע פעולות של סופר יוזר
    username: tal
    password: tal

Pay pal payment:
    email: sb-k45wf20360149@personal.example.com
    password: R>(b{2k]

REMAMBER:
    כל הקישורים באתר רלוונטים ויש אותם גם בהדר וגם בפוטר לא לפספס !׳
"""



# Create your views here.


def home(request):
    """
    Home page
    """
    data = Product.objects.filter(is_featured=True).order_by('-id')
    banners = Banner.objects.all().order_by('-id')
    return render(request,'index.html',{'data':data,'banners':banners})



def register1(request,staff=False):
    """
    Register + Welcome email + Confirm email (the rdirect from here is to login)
    """
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        # User checks for regisretions
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Try other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "The Email already exist! try new email")
            return redirect('home')

        if len(username) > 20:
            messages.error(request, "user name must be less than 20 charecters")

        if pass1 != pass2:
            messages.error(request, "Password didn't match!")
        #end

        if staff == True:
            myuser = User.objects.create_user(username, email, pass1,is_superuser=staff,is_staff=staff)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.is_active = False
            myuser.save()
        else:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.is_active = False
            myuser.save()

        messages.success(request, "Your Account successfully created, We have sent you a confirmation email, please confirm your email adress for activate your account")

        # Welcome email
        subject = "Welcome to the biggest brand Moontag"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Moontag  \n We have sent you a confirmation email, please confirm your email adress for activate your account \n\n Thank you ! \n Moontag Brand "
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Adress confirm
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ moontag - django login!"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),  
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()

        return redirect('login1')
    if staff == True:
        staff_html = 'Staff'
    else:
        staff_html = ' '

    return render(request,'register.html',{'staff':staff_html})



def login1(request):
    """
    Login
    """
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            data = Product.objects.filter(is_featured=True).order_by('-id')
            banners = Banner.objects.all().order_by('-id')
            return render(request, "index.html", {'fname': fname,'data':data,'banners':banners})

        else:
            messages.error(request, 'Bed credentials')
            return redirect('home')


    return render(request,'login.html')


  
def logout1(request):
    """
    Logout
    """
    logout(request)
    messages.success(request, "You are logged out")
    return redirect('/')



def activate(request, uidb64, token):
    """
    Active User
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')



def categories(request):
    """
    category list
    """
    category_data = Category.objects.all().order_by('-id')
    return render(request, 'category.html',{'data':category_data})



def brands(request):
    """
    Brands list
    """
    brands_data = Brand.objects.all().order_by('-id')
    return render(request, 'brand.html',{'data':brands_data})



def product_list(request):
    """
    Product list
    """
    product_data = Product.objects.all().order_by('-id')
    return render(request, 'product_list.html',{'data':product_data})



def category_product_list(request,cat_id):
    """
    Product list per category
    """
    category = Category.objects.get(id=cat_id)
    data = Product.objects.filter(category=category).order_by('-id')
    return render(request, 'category_product_list.html',{'data':data})



def brand_product_list(request,brand_id):
    """
    Product list per brand
    """
    brand = Brand.objects.get(id=brand_id)
    data = Product.objects.filter(brand=brand).order_by('-id')
    return render(request, 'category_product_list.html',{'data':data})



def product_page(request,slug,id):
    """
    Product page for every product
    """
    if request.method == "POST":
        username = request.POST['username']
        product_name = request.POST['product']
        review_comment = request.POST['comment']
        stars = request.POST['stars']
        review = ProductReview(user=username,product=product_name,review_text=review_comment,review_rating=stars)
        review.save()

    product = Product.objects.get(id=id)
    rewiews = ProductReview.objects.filter(product=product).order_by('-id')
    if len(rewiews) != 0:
        get_avg_rating = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating')) # Get the avg for the product ratings
        avg_rating = "%.1f" % get_avg_rating['avg_rating'] # Short to only one digit after the dot
    else:
        avg_rating = 'Still Dont Have Reviews'
    
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4] # exclude for not show the same product in the related products.
    colors = ProductAttribute.objects.filter(product=product).values('color__id','color__title','color__color_code').distinct() # values mean i am getting the colums and i want to distinct the data
    sizes = ProductAttribute.objects.filter(product=product).values('size__id','size__title','price','color__id').distinct()
    return render(request, 'product_page.html',{'data':product,'related_products':related_products,'colors':colors,'sizes':sizes,'rewiews':rewiews,'avg':avg_rating})



def search_result(request):
    """
    Search result for the search box in the header
    """
    q = request.GET['q']
    data = Product.objects.filter(title__icontains=q).order_by('id')
    return render(request,'search_result.html',{'data':data})



def filter_data(request):
    """
    filter for the sidebar in the product list pages that include a sidebar of filters i am using hare also AJAX and JS.
    """
    colors = request.GET.getlist('color[]')
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    minPrice = request.GET['minPrice']
    maxPrice = request.GET['maxPrice']
    all_products = Product.objects.all().order_by('-id').distinct() # becuase product can be in two colors we need put the distinct() function to fach them and dont show the same product that he have the same attribute
    all_products = all_products.filter(productattribute__price__gte=minPrice)
    all_products = all_products.filter(productattribute__price__lte=maxPrice)
    if len(colors) > 0:
        all_products = all_products.filter(productattribute__color__id__in=colors).distinct()
    if len(categories) > 0:
        all_products = all_products.filter(category__id__in=categories).distinct()
    if len(brands) > 0:
        all_products = all_products.filter(brand__id__in=brands).distinct()
    if len(sizes) > 0:
        all_products = all_products.filter(productattribute__size__id__in=sizes).distinct()   
    t = render_to_string('ajax/product-list.html',{'data':all_products})
    return JsonResponse({'data':t})



def add_to_cart(request):
    """
    Add to cart function also with help of ajax and Javascript
    """
    cart_product = {}
    cart_product[str(request.GET['id'])] = {
        'img':request.GET['img'],
        'title':request.GET['title'],
        'qty':request.GET['qty'],
        'price':request.GET['price'],
    }

    if 'cartdata' in request.session:
        if str(request.GET['id']) in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty']) # For get the qty from the user
            cart_data.update(cart_data)
            request.session['cartdata'] = cart_data
        else:
            cart_data = request.session['cartdata'] # getting the data
            cart_data.update(cart_product) # if dict not exist the update add him to the dict that exict
            request.session['cartdata'] = cart_data # adding in the session
    else:
        request.session['cartdata'] = cart_product
    return JsonResponse({'data':request.session['cartdata'],'total_items':len(request.session['cartdata'])})



def cart_page(request):
    """
    Cart page with all the things like - total price of all the Products, 
    """
    total_price = 0
    for p_id,item in request.session['cartdata'].items():
        total_price += int(item['qty']) * float(item['price'])
    return render(request,'cart.html',{'cart_data':request.session['cartdata'],'total_items':len(request.session['cartdata']),'total_price':total_price})



def delete_cart_item(request):
    """
    Delete items from cart with help of ajax & java script 
    """
    p_id = str(request.GET['id'])
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            del request.session['cartdata'][p_id]
            request.session['cartdata'] = cart_data
    total_price = 0
    for p_id,item in request.session['cartdata'].items():
        total_price += int(item['qty']) * float(item['price']) # Becuase i change the template with the respone and delete i need to do the same calculate in the new template
    t = render_to_string('ajax/cart_page.html',{'cart_data':request.session['cartdata'],'total_items':len(request.session['cartdata']),'total_price':total_price})
    return JsonResponse({'data':t,'total_items':len(request.session['cartdata'])})



def update_cart_item(request):
    """
    update items from cart with help of ajax & java script 
    """
    p_id = str(request.GET['id'])
    p_qty = request.GET['qty']
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data = request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty'] = p_qty
            request.session['cartdata'] = cart_data
    total_price = 0
    for p_id,item in request.session['cartdata'].items():
        total_price += int(item['qty']) * float(item['price']) # Becuase i change the template with the respone and delete i need to do the same calculate in the new template
    t = render_to_string('ajax/cart_page.html',{'cart_data':request.session['cartdata'],'total_items':len(request.session['cartdata']),'total_price':total_price})
    return JsonResponse({'data':t,'total_items':len(request.session['cartdata'])})



@login_required
def checkout(request):
    """
    Checkout page after the Cart page + if someone reach to the page i save it and can check after that if he buy after the checkout
    """
    total_price = 0
    totalPrice = 0
    if 'cartdata' in request.session:
        for p_id,item in request.session['cartdata'].items():
            totalPrice += int(item['qty']) * float(item['price'])
        order = CartOrder.objects.create(user=request.user,total_amt=totalPrice)
        for p_id,item in request.session['cartdata'].items():
            total_price += int(item['qty']) * float(item['price'])
            items = CartOrderItems.objects.create(order=order,in_num='INV-'+str(order.id),item=item['title'],img=item['img'],qty=item['qty'],price=item['price'],total=float(item['qty'])*float(item['price']))
        host = request.get_host()
        paypal_dict = {'business':settings.PAYPAL_RECIVER_EMAIL,'amount':total_price,'item_name':'OrderNum-'+str(order.id),'invoice':'INV-'+str(order.id),'currency_code':'USD','notify_url':'http://{}{}'.format(host,reverse('paypal-ipn')),'return_url':'http://{}{}'.format(host,reverse('payment_done')),'cancel_return':'http://{}{}'.format(host,reverse('payment_cancelled'))}
        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request,'checkout.html',{'cart_data':request.session['cartdata'],'total_items':len(request.session['cartdata']),'total_price':total_price,'form':form})



@csrf_exempt
def payment_done(request):
    """
    Payment done Page and View the order detail that you paid
    """
    return_data=request.POST
    order = CartOrder.objects.last()
    order.paid_status = True
    order.save()
    order = CartOrder.objects.last()
    orders = CartOrder.objects.filter(order_dt=order.order_dt)
    return render(request, 'payment-success.html',{'data':return_data,'orders':orders})
	


@csrf_exempt
def payment_canceled(request):
    """
    Payment canceled Page
    """
    return render(request, 'payment-fail.html')



@login_required
def add_product(request):
    """
    Add product
    """
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Product successfully created.")
    form = ProductForm
    return render(request, 'add_product.html',{'form':form})



@login_required
def add_category(request):
    """
    Add Category
    """
    if request.method == "POST" and request.FILES['img']:
        title = request.POST['title']
        img = request.FILES['img']
        category = Category(title=title,img=img)
        category.save()
        messages.success(request, "Your Category successfully created.")
    return render(request,'add_category.html')



@login_required
def add_brand(request):
    """
    Add Brand
    """
    if request.method == "POST" and request.FILES['img']:
        title = request.POST['title']
        img = request.FILES['img']
        brand = Brand(title=title,img=img)
        brand.save()
        messages.success(request, "Your Brand successfully created.")
    return render(request,'add_brand.html')



@login_required
def add_attribute(request):
    """
    Add product attribute - Have to do it if you want show the product properly
    """
    if request.method == "POST" and request.FILES['img']:
        form = ProductAttributeForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Attribute successfully created.")
        else:
            messages.error(request, "Dont saved please check again or try later")
    form = ProductAttributeForm
    return render(request, 'add_attribute.html',{'form':form})



@login_required
def add_color(request):
    """
    Add Color
    """
    if request.method == "POST":
        title = request.POST['title']
        color_code = request.POST['color_code']
        color = Color(title=title,color_code=color_code)
        color.save()
        messages.success(request, "Your Color successfully created.")
    return render(request,'add_color.html')



@login_required
def add_size(request):
    """
    Add Size
    """
    if request.method == "POST":
        title = request.POST['title']
        size = Size(title=title)
        size.save()
        messages.success(request, "Your Size successfully created.")
    return render(request,'add_size.html')



@login_required
def add_banner(request):
    """
    Add Banner
    """
    if request.method == "POST" and request.FILES['img']:
        img = request.FILES['img']
        text = request.POST['text']
        banner = Banner(img=img,text=text)
        banner.save()
        messages.success(request, "Your Banner successfully created.")
    return render(request,'add_banner.html')



def user_dashboard(request):
    """
    User dashboard, he or she can see orders and logout
    """
    return render(request, 'user_dashboard.html')



def user_orders(request):
    """
    After click on the your orders in the dashboard page
    """
    orders = CartOrder.objects.filter(user=request.user,paid_status=True).order_by('-id')
    return render(request, 'user_orders.html',{'orders':orders})



def user_orders_items(request,id):
    """
    You can click in the user order on the order number and fet the items from the order
    """
    order = CartOrder.objects.get(pk=id)
    orders_items = CartOrderItems.objects.filter(order=order).order_by('-id')
    return render(request, 'user_orders_items.html',{'orders_items':orders_items})



def order_search(request):
    """
    Order search in the dashboard Panel / User orders
    """
    q = request.GET['q']
    orders = CartOrder.objects.filter(total_amt=q).order_by('-id')
    return render(request, 'order_search.html',{'orders':orders})
 
    

def checkout_purchasing(request):
    """
    Pepole that get to the checkout page and dont buy + more table with pepole that Buy
    """
    orders = CartOrder.objects.all()
    return render(request, 'checkout_purchasing.html',{'orders':orders})



@login_required
def display_product(request):
    """
    View all the products and Remove option 
    """
    products = Product.objects.all().order_by('-id')
    if request.method == "POST":
        id = request.POST['id']
        product = Product.objects.get(id=id)
        product.delete()
        messages.success(request, 'The product removed')
    return render(request, 'display_product.html',{'products':products})



def data(request):
    """
    Data on the website 
    """
    a = CartOrder.objects.filter(paid_status=True).aggregate(Sum('total_amt'))
    avg = ProductAttribute.objects.aggregate(Avg('price'))
    total_products = Product.objects.all()
    return render(request, 'data.html', {'avg':avg,'total_products':total_products,'total_price':a})



@csrf_exempt
def add_wishlist(request):
    """
    Add To Wishlist Product process
    """
    if request.method == 'POST':
        pid = json.loads(request.body)
        product = Product.objects.get(pk=pid['productId'])
        data = {}
        check_product = Wishlist.objects.filter(product=product,user=request.user).count()
        if check_product > 0:
            data = {
                'bool': False
            }
        else:
            wishliast = Wishlist.objects.create(product=product,user=request.user)
            data = {
                'bool': True
            }
    return JsonResponse(data)



def wishlist(request):
    """
    Wishlist Section
    """
    if request.method == 'POST':
        pid = request.POST['id']
        remove_product = Wishlist.objects.get(product=pid)
        remove_product.delete()
        messages.success(request, 'Removed From Wishlist')
    products = Wishlist.objects.filter(user=request.user).order_by('-id')
    return render(request, 'wishlist.html',{'products':products})



@login_required
def welcome (request):
    """
    Weoclome page React - Username
    """
    user = request.user
    return render(request, 'marketplace/welcome.html', {'user':user})



@login_required
def store_register(request):
    """
    Vendors Register they store
    """
    if request.method == 'POST' and request.FILES['storeImage']:
        store_name = request.POST['storeName']
        company_name = request.POST['companyName']
        store_image = request.FILES['storeImage']
        business_email = request.POST['businessEmail']
        payPal_email = request.POST['payPalEmail']
        if Vendors.objects.filter(store_name=store_name):
                messages.error(request, "Store already exist! Try other Store Name")
                return redirect('home')
        else:
            brand = Brand.objects.create(title=store_name,img=store_image)
            brand.save()
            vendor = Vendors.objects.create(user=request.user,store_name=store_name,company_name=company_name,store_img=store_image,business_email=business_email,pay_pal=payPal_email)
            vendor.save()
            messages.success(request, 'The Store Created')
            return redirect('/store')
    return render(request, 'marketplace/store_register.html')



def store(request):
    """
    Vendor Admin Panel With many of the data
    """
    if len(Vendors.objects.filter(user=request.user)) > 0:
        vendor = Vendors.objects.get(user=request.user)
        todos = Todo.objects.filter(user=request.user)
        vendor_products = VendorAddProduct.objects.filter(user=request.user)
        li = []
        for i in vendor_products:
            products = CartOrderItems.objects.filter(item=i.product).exclude(order__paid_status=False)
            li.append(products)
        total_sales = 0
        for item in li:
            for p in item:
                orders = CartOrder.objects.filter(id=int(p.in_num[4:]))
                total_sales += p.total
        after_moontag_commission = total_sales - (int(total_sales) * 0.17)
        if request.method == 'POST':
            new_task = request.POST['todo']
            save_task = Todo.objects.create(user=request.user,todo=new_task)
            save_task.save()
        return render(request, 'marketplace/index.html', {'user':request.user,'vendor':vendor,'products':li,'total_sales':total_sales,'commission':after_moontag_commission,'todos':todos,'orders':orders,'vendor_products':vendor_products})
    else:
        return redirect('/store-register')



def order_details(request,id):
    """
    Order Details in Vendor Store
    """
    orders = CartOrderItems.objects.filter(order_id=id)
    return render(request, 'marketplace/orders_detail.html',{'orders':orders})



def delete_todo(request):
    """
    Delete Todo task in Admin marketplace panel
    """
    if request.method == 'POST':
        todo_id = request.POST['todoId']
        todo = Todo.objects.get(id=todo_id)
        todo.delete()
        return redirect('/store')
 


def vendor_add_product(request):
    """
    Vendor Add his Products
    """
    user = request.user
    vendor = Vendors.objects.get(user=request.user)
    categories = Category.objects.all()
    brands = Brand.objects.get(title=vendor.store_name)
    colors = Color.objects.all()
    sizes = Size.objects.all()
    if request.method == 'POST':
        title = request.POST['title']
        slug = request.POST['slug']
        detail = request.POST['detail']
        specs = request.POST['specs']
        category = Category.objects.get(id=request.POST['category'])
        brand = Brand.objects.get(id=request.POST['brand'])
        color =  Color.objects.get(id=request.POST['color']) 
        size = Size.objects.get(id=request.POST['size'])
        product = Product.objects.create(title=title,slug=slug,detail=detail,specs=specs,category=category,brand=brand,color=color,size=size,status=True,is_featured=False)
        product.save()
        new_added_product = Product.objects.last()
        vendor_add_product_model = VendorAddProduct.objects.create(user=request.user,product=new_added_product)
        vendor_add_product_model.save()
        messages.success(request, 'Product Added Succefuly Remamber To add Atribute if you want the product will be displayed on our store')
        return redirect('/store/add-attribute')
    return render(request, 'marketplace/add_product.html', {'user':user,'vendor':vendor,'category':categories,'brand':brands,'colors':colors,'sizes':sizes})



def vendor_add_attribute(request):
    """
    Add Attribute for vendor products
    """
    user = request.user
    vendor = Vendors.objects.get(user=request.user)
    user_brand = Brand.objects.get(title=vendor.store_name)
    products = Product.objects.filter(brand=user_brand.id)
    colors = Color.objects.all()
    sizes = Size.objects.all()
    if request.method == "POST" and request.FILES['img']:
        product = Product.objects.get(id=request.POST['product'])
        color = Color.objects.get(id=request.POST['color'])
        size = Size.objects.get(id=request.POST['size'])
        price = request.POST['price']
        img = request.FILES['img']
        product_attribute = ProductAttribute.objects.create(product=product,color=color,size=size,price=price,img=img)
        product_attribute.save()
        messages.success(request, 'Attribute Added Succefuly')
    return render(request, 'marketplace/add_attribute.html', {'user':user,'vendor':vendor,'products':products,'colors':colors,'sizes':sizes})



def store_products(request):
    """
    Store Products section
    """
    user = request.user
    vendor = Vendors.objects.get(user=request.user)
    products = VendorAddProduct.objects.filter(user=request.user)
    return render(request, 'marketplace/products.html', {'user':user,'vendor':vendor,'products':products})



def vendor_edit_product(request,id):
    """
    Vendor Edit his Products
    """
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        title = request.POST['title']
        slug = request.POST['slug']
        detail = request.POST['detail']
        specs = request.POST['specs']
        Product.objects.filter(id=id).update(title=title,slug=slug,detail=detail,specs=specs)
        return redirect('/store/products')
    return render(request, 'marketplace/edit_product.html', {'product':product})



def withraw(request):
    """
    Vendor Withraw (Get Paid for his sales)
    """
    vendor = Vendors.objects.get(user=request.user)
    vendor_products = VendorAddProduct.objects.filter(user=request.user)
    li = []
    for i in vendor_products:
        products = CartOrderItems.objects.filter(item=i.product).exclude(order__paid_status=False)
        li.append(products)
    total_sales = 0
    for item in li:
        for p in item:
            total_sales += p.total
    after_moontag_commission = total_sales - (int(total_sales) * 0.17)
    user_withraws = Withraw.objects.filter(user=request.user)
    what_paid = 0
    for y in user_withraws:
        what_paid += int(y.amount)
    after_moontag_commission -= what_paid
    if request.method == 'POST':
        withraw_request = request.POST['withraw']
        withraw_request_save = Withraw.objects.create(user=request.user,amount=withraw_request)
        withraw_request_save.save()
        return redirect('/store/withraw')
    return render(request, 'marketplace/withraw.html',{'vendor':vendor,'user':request.user,'after_moontag_commission':after_moontag_commission,'total_sales':total_sales,'paid':what_paid})





