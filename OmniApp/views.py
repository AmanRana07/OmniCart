# views.py

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.views import View
from .forms import *
from django.db.models import Q, Count
from .models import Customer, Order
from django.contrib.auth.hashers import check_password
from django.urls import reverse
import re
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from uuid import UUID
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def authentication_login(request):
    customer_session = request.session.get("customer")

    if customer_session:
        customer_id = customer_session.get("id")
        try:
            # Try to fetch the customer if the ID is available
            customer = Customer.objects.get(id=customer_id)
            user_authenticated = True
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist
            user_authenticated = False
            customer = None
    else:
        # Customer session is not available, user is not authenticated
        user_authenticated = False
        customer = None
    types = customer.user_type if customer else None
    return user_authenticated, types


def index(request):
    # Get the customer session from the session
    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/index.html", context)


# def cart_view(request):
#     customer_id = request.session.get("customer")
#     # Check if the customer is authenticated
#     user_authenticated = customer_id is not None

#     context = {
#         "user_authenticated": user_authenticated,
#         "current_page_url": request.path,
#     }
#     return render(request, "OmniCart/cart.html", context)


class CustomLoginView(View):
    template_name = "OmniCart/Authintication/login.html"
    return_url = None

    def get(self, request):
        CustomLoginView.return_url = request.GET.get("return_url")
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("username")
        password = request.POST.get("password")

        if re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email):
            customer = Customer.get_customer_by_email(email)
        else:
            customer = Customer.get_customer_by_username(email)

        error_message = None
        user_type = None

        if customer and check_password(password, customer.password):
            # Convert the UUID to a string before storing it in the session
            request.session["customer"] = {
                "id": str(customer.id),
                "username": customer.username,
            }
            user_type = customer.user_type

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                if customer.user_type == "manufacturer":
                    # Redirect to the manufacturer admin panel
                    return redirect(
                        reverse("admin_panel", kwargs={"customer_id": str(customer.id)})
                    )
                else:
                    if CustomLoginView.return_url:
                        return HttpResponseRedirect(CustomLoginView.return_url)
                    else:
                        CustomLoginView.return_url = None
                        # Redirect to the home page or another named URL
                        return redirect("index")
            else:
                error_message = "Authentication failed"
        else:
            error_message = "Invalid login credentials"

        context = {
            "type": user_type,
            "customer": customer,
            "error_message": error_message,
            "user_authenticated": False,
        }

        return render(request, self.template_name, context)


class RegistrationView(View):
    template_name = "OmniCart/Authintication/register.html"

    def get(self, request):
        form = CustomerCreationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomerCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])  # Use 'password1' here
            user.save()
            User = get_user_model()
            new_user = User.objects.create_user(
                username=user.username,
                email=user.email,
                password=form.cleaned_data["password1"],
            )
            new_user.save()
            return redirect("login")  # Change 'login' to your login URL

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    template_name = "OmniCart/Authintication/logout.html"

    def get(self, request):
        request.session.clear()
        logout(request)
        return redirect("login")

    def post(self, request):
        # You can add addition
        return self.get(request)


class AdminPanelView(View):
    template_name = "OmniCart/admin/admin_panel.html"

    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")

            # Get the total number of products and customers
            total_products = Product.objects.filter(manufacturer_id=customer).count()

            return render(
                request,
                self.template_name,
                {
                    "customer": customer,
                    "total_products": total_products,
                    # "total_customers": total_customers,
                },
            )
        except Customer.DoesNotExist:
            # Handle the case where the customer or user type does not exist
            return render(
                request,
                "OmniCart/error.html",
                {"error_message": "Invalid customer ID or user type."},
            )


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        customer_session = request.session.get("customer")
        if customer_session:
            if form.is_valid():
                product = form.save(commit=False)

                # Retrieve the logged-in customer (manufacturer)
                customer_id = customer_session.get("id")
                customer = Customer.objects.get(
                    id=customer_id, user_type="manufacturer"
                )

                # Set the manufacturer to the currently logged-in user
                product.manufacturer_id = customer
                product.save()

                messages.success(request, "Product added successfully!")
                return redirect("add_product")
            else:
                error_message = "There was an error. Please check the form."
    else:
        form = ProductForm()
        error_message = None

    return render(
        request,
        "OmniCart/admin/add_product.html",
        {"form": form, "error_message": error_message},
    )


# Listing of all the Produts
def product_list(request):
    # Check if the customer is logged in and is a manufacturer
    customer_session = request.session.get("customer")

    if customer_session:
        customer_id = customer_session.get("id")
        try:
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")
            # Filter products based on the manufacturer ID
            products = Product.objects.filter(manufacturer_id=customer)
            return render(
                request, "OmniCart/admin/product_list.html", {"products": products}
            )
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist or is not a manufacturer
            messages.error(request, "Invalid customer or not a manufacturer.")
            return redirect("login")  # Redirect to the login page or handle as needed
    else:
        # Handle the case where the customer is not logged in
        messages.error(request, "Please log in as a manufacturer.")
        return redirect("login")  # Redirect to the login page or handle as needed


def product_edit(request, product_id):
    customer_session = request.session.get("customer")
    # Retrieve the product object
    product = get_object_or_404(Product, product_id=product_id)
    if customer_session:
        if request.method == "POST":
            # Populate the form with the submitted data and instance
            form = ProductEditrm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                # Save the updated data
                form.save()
                return redirect(
                    "product_list"
                )  # Redirect to the product list page after successful update
        else:
            # Populate the form with the current product data
            form = ProductEditrm(instance=product)
        return render(
            request,
            "OmniCart/admin/product_edit.html",
            {"form": form, "product": product},
        )
    else:
        # Handle the case where the customer is not logged in
        messages.error(request, "Please log in as a manufacturer.")
        return redirect("login")


def product_delete(request, product_id):
    customer_session = request.session.get("customer")

    product = get_object_or_404(Product, product_id=product_id)

    # Check if the request method is POST
    if request.method == "POST":
        # Delete the product
        product.delete()

        # Return a JSON response indicating success
        return JsonResponse({"message": "Product deleted successfully."})

    # Return a JSON response indicating an error (this should not happen in a valid scenario)
    return JsonResponse({"error": "Invalid request method."}, status=400)


def shop(request):
    # Assuming you have a queryset for products and categories
    products = Product.objects.all()
    # categories = Category.objects.all()
    customer_id = request.session.get("customer")
    # Check if the customer is authenticated
    user_authenticated = customer_id is not None
    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 9)  # Show 9 products per page
    try:
        product_pages = paginator.page(page)
    except PageNotAnInteger:
        product_pages = paginator.page(1)
    except EmptyPage:
        product_pages = paginator.page(paginator.num_pages)

    context = {
        "products": product_pages,
        # 'categories': categories,
        "user_authenticated": user_authenticated,
        "current_page": int(page),
        "product_pages": range(1, product_pages.paginator.num_pages + 1),
    }

    return render(request, "OmniCart/product/shop.html", context)


# Order View
def order_list(request):
    # Check if the logged-in user is a manufacturer
    customer_session = request.session.get("customer")

    if customer_session:
        customer_id = customer_session.get("id")
        try:
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")
            # Filter products based on the manufacturer ID
            products = Product.objects.filter(manufacturer_id=customer)
            orders = Order.objects.filter(items__product__in=products).distinct()
            return render(
                request, "OmniCart/admin/order/view-order.html", {"orders": orders}
            )
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist or is not a manufacturer
            messages.error(request, "Invalid customer or not a manufacturer.")
            return redirect("login")  # Redirect to the login page or handle as needed
    else:
        # Handle the case where the customer is not logged in
        messages.error(request, "Please log in as a manufacturer.")
        return redirect("login")


def order_detail(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)
    # print(order.user_id)
    # Retrieve the customer who placed the order
    customer = get_object_or_404(User, id=order.user_id)
    customers = Customer.objects.get(email=customer.email)

    # You can customize this context based on your requirements
    context = {
        "order": order,
        "customer": customers,
    }

    return render(request, "OmniCart/admin/order/order_detail.html", context)


def update_order_status(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # Get the new status from the form
        new_status = request.POST.get("status")
        if new_status:
            # Update the order status
            order.status = new_status
            order.save()
            # Redirect back to the order list page
            return redirect("order_list")

    # If the request method is not POST or status is not provided, redirect back to the order list page
    return redirect("order_list")


def shops(request):
    # Assuming you have a queryset for products and categories
    products = Product.objects.all()
    user_authenticated, types = authentication_login(request)
    # categories = Category.objects.all()

    # Pagination
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 9)  # Show 9 products per page
    try:
        product_pages = paginator.page(page)
    except PageNotAnInteger:
        product_pages = paginator.page(1)
    except EmptyPage:
        product_pages = paginator.page(paginator.num_pages)

    context = {
        "products": product_pages,
        # 'categories': categories,
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page": int(page),
        "product_pages": range(1, product_pages.paginator.num_pages + 1),
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/shops.html", context)


def product_detail(request, product_id):
    # Retrieve the product details based on the product_id
    product = get_object_or_404(Product, product_id=product_id)

    context = {
        "product": product,
    }

    return render(request, "OmniCart/product/product_detail.html", context)


@login_required(login_url="login")
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    user = request.user

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=user)

    # Check if the product is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    # If the item is already in the cart, increase the quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@login_required(login_url="login")
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    user_authenticated, types = authentication_login(request)

    context = {
        "cart": cart,
        "user_authenticated": user_authenticated,
        "type": types,
    }

    return render(request, "OmniCart/cart.html", context)


def update_cart_quantity(request, item_id, new_quantity):
    try:
        # Get the CartItem based on the item_id
        cart_item = CartItem.objects.get(id=item_id)

        # Update the quantity
        cart_item.quantity = new_quantity
        cart_item.save()

        # Update the total price and quantity in the Cart
        cart_item.cart.update_total()

        return JsonResponse({"success": True})
    except CartItem.DoesNotExist:
        return JsonResponse({"success": False, "message": "CartItem does not exist"})


def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()

        return JsonResponse({"success": True})
    except CartItem.DoesNotExist:
        return JsonResponse({"success": False, "message": "CartItem does not exist"})


# Now Checkout page


@login_required(login_url="login")
def checkout(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    user_authenticated, types = authentication_login(request)

    customer_session = request.session.get("customer")
    customer_id = customer_session.get("id") if customer_session else None

    if customer_id:
        customer = Customer.objects.get(id=customer_id)
    else:
        customer = None

    if request.method == "POST":
        try:
            # Create a new order
            order = Order.objects.create(user=user, total_price=cart.total_price)

            # Move cart items to order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.product.unit_price,
                )

            # Clear the cart
            cart_items = cart.items.all()

            # Delete cart items individually using filter
            for cart_item in cart_items:
                cart_item.delete()

            # Delete the cart
            cart.delete()

            # Redirect to a success page
            return redirect(reverse("order_success", kwargs={"order_id": order.id}))

        except Exception as e:
            print(f"Error during checkout: {e}")

    context = {
        "cart": cart,
        "user_authenticated": user_authenticated,
        "customer": customer,
        "type": types,
    }
    return render(request, "OmniCart/checkout.html", context)


def order_success(request, order_id):
    # Fetch the order and customer information
    try:
        order = Order.objects.get(id=order_id)
        user_authenticated, types = authentication_login(request)
        customer_session = request.session.get("customer")
        customer_id = customer_session.get("id") if customer_session else None

        if customer_id:
            customer = Customer.objects.get(id=customer_id)
        else:
            customer = None

    except Order.DoesNotExist or Customer.DoesNotExist:
        return redirect("index")

    context = {
        "order": order,
        "customer": customer,
        "user_authenticated": user_authenticated,
        "type": types,
    }

    return render(request, "OmniCart/order_success.html", context)

    
def shipping(request):
    
    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request,'OmniCart/info/shipping.html',context)

def privacy(request):
    
    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request,'OmniCart/info/privacy.html',context)

def pymntmethods(request):
    
    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request,'OmniCart/info/pymntmethods.html',context)

def returns(request):
    
    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request,'OmniCart/info/returns.html',context)

def moneyback(request):
    
    user_authenticated, types = authentication_login(request)
    context = {
        "user_authenticated": user_authenticated,
        "type": types,
    }
    return render(request,'OmniCart/info/moneyback.html',context)


def about_us(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/aboutus.html", context)

def contact_us(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/contactus.html", context)

def faq(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/faq.html", context)

def help(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/help.html", context)

def terms_and_condition(request):

    user_authenticated, types = authentication_login(request)

    context = {
        "user_authenticated": user_authenticated,
        "type": types,
        "current_page_url": request.path,
    }

    return render(request, "OmniCart/product/termsandcondition.html", context)