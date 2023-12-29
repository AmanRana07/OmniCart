# views.py

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views import View
from .forms import *
from django.db.models import Q
from .models import Customer
from django.contrib.auth.hashers import check_password
from django.urls import reverse
import re
from django.contrib import messages


def index(request):
    # Get the customer ID from the session
    customer_session = request.session.get("customer")
    customer_id = customer_session.get("id")

    if customer_id:
        try:
            # Try to fetch the customer if the ID is available
            customer = Customer.objects.get(id=customer_id)
            user_authenticated = True
        except Customer.DoesNotExist:
            # Handle the case where the customer does not exist
            user_authenticated = False
    else:
        # Customer ID is not available, user is not authenticated
        user_authenticated = False

    context = {
        "user_authenticated": user_authenticated,
        "type": customer.user_type,
    }

    return render(request, "OmniCart/index.html", context)


def cart_view(request):
    customer_id = request.session.get("customer")
    # Check if the customer is authenticated
    user_authenticated = customer_id is not None

    context = {
        "user_authenticated": user_authenticated,
    }
    return render(request, "OmniCart/cart.html", context)


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
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                # Convert the UUID to a string before storing it in the session
                request.session["customer"] = {
                    "id": str(customer.id),
                    "username": customer.username,
                }
                user_type = customer.user_type
                # cursor = connection.cursor()

                if customer.user_type == "manufacturer":
                    # Redirect to the manufacturer admin panel
                    return redirect("admin_panel", customer_id=str(customer.id))
                else:
                    if CustomLoginView.return_url:
                        return HttpResponseRedirect(CustomLoginView.return_url)
                    else:
                        CustomLoginView.return_url = None
                        # Redirect to the home page or another named URL
                        return redirect("index")
                    # return redirect("index")  # Change 'home' to your home URL name
            else:
                error_message = "Password is not Correct!! Please Check the Password:)"
        else:
            error_message = "Invalid login credentials"

        context = {
            "type": user_type,
            "customer": customer,
            "error_message": error_message,
            "user_authenticated": False,  # Set authentication status to False on login failure
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

            return redirect("login")  # Change 'login' to your login URL

        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    template_name = "OmniCart/Authintication/logout.html"

    def get(self, request):
        request.session.clear()
        return redirect("login")

    def post(self, request):
        # You can add addition
        return self.get(request)


class AdminPanelView(View):
    template_name = "OmniCart/admin/admin_panel.html"

    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")
        except Customer.DoesNotExist:
            # Handle the case where the customer or user type does not exist
            return render(
                request,
                "OmniCart/error.html",
                {"error_message": "Invalid customer ID or user type."},
            )

        return render(request, self.template_name, {"customer": customer})


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        customer_session = request.session.get("customer")
        if form.is_valid():
            product = form.save(commit=False)

            # Retrieve the logged-in customer (manufacturer)
            customer_id = customer_session.get("id")
            customer = Customer.objects.get(id=customer_id, user_type="manufacturer")

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
    # Retrieve the product object
    product = get_object_or_404(Product, product_id=product_id)

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
        request, "OmniCart/admin/product_edit.html", {"form": form, "product": product}
    )
