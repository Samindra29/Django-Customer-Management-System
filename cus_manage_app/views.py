from http.client import ImproperConnectionState
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse
from django.forms import inlineformset_factory

from cus_manage_app.decorators import *
from .models import *
from .forms import *
from .filters import *

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


# registration page

@authenticated_user
def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user = user,
            )

            messages.success(request,'Hello ' + username + ' your account has been created successfully!' )
            return redirect('login')
             

    context = {'form': form}
    return render(request, 'register.html', context)



# login page

@authenticated_user
def loginPage(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.info(request, 'Username or Passowrd is incorrect')

    context = {}
    return render(request, 'login.html', context)


# logout page
def logoutUser(request):
    logout(request)
    return redirect('login')



# user page
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])

def userPage(request):
    orders = request.user.customer.order_set.all()  
    total_orders = orders.count()
    orders_delivered = orders.filter(status='Delivered').count()
    orders_pending = orders.filter(status='Pending').count()
    orders_out_for_delivery = orders.filter(status='Out for Delivery').count()


    context = {
        'orders': orders, 
        'total_orders' : total_orders,
        'orders_delivered': orders_delivered,
        'orders_pending': orders_pending,
        'orders_out_for_delivery': orders_out_for_delivery
    }
    return render(request, 'user.html', context)

# user profile page
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])

def userProfile(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid:
            form.save()

    context = {'form': form}
    return render(request, 'user_profile.html', context)



# home page
@login_required(login_url='login')
@admin_only

def home(request):
    customer = Customer.objects.all()
    orders = Order.objects.all()

    total_orders = orders.count()
    orders_delivered = orders.filter(status='Delivered').count()
    orders_pending = orders.filter(status='Pending').count()
    orders_out_for_delivery = orders.filter(status='Out for Delivery').count()

    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'orders_delivered': orders_delivered,
        'orders_pending': orders_pending,
        'orders_out_for_delivery': orders_out_for_delivery
        }

    return render(request, 'dashboard.html', context)



# products page
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})



# customer info page
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {
        'customer': customer,
        'orders': orders, 
        'order_count': order_count,
        'myFilter':  myFilter
        }
    return render(request, 'customer.html', context)


# create customer order
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def createOrder(request, pk):

    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)

    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form = OrderForm(initial={'customer': customer})

    if request.method == "POST":
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    # context = {'form': form}
    context = {'formset': formset}
    return render(request, 'order_form.html', context)


# update customer order
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'order_form.html', context)


# delete customer order
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == "POST":
        order.delete()
        return redirect('/')

    context = {'item': order}
    return render(request, 'delete.html', context)