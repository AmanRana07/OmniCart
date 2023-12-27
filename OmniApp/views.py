# views.py

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.views import View
from .forms import CustomerCreationForm
from django.db.models import Q
from .models import Customer
from django.contrib.auth.hashers import check_password
from django.urls import reverse
import re


def index(request):
    # Get the customer ID from the session
    customer_id = request.session.get("customer")
    # Check if the customer is authenticated
    user_authenticated = customer_id is not None

    context = {
        "user_authenticated": user_authenticated,
    }

    return render(request, "OmniCart/index.html", context)


def cart_view(request):
    customer_id = request.session.get("customer")
    # Check if the customer is authenticated
    user_authenticated = customer_id is not None

    context = {
        "user_authenticated": user_authenticated,
    }
    return render(request, "OmniCart/index.html", context)


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
                request.session["customer"] = str(customer.id)

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
