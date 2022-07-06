from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import OrderForm,CreateUserForm
from .filters import *

# Create your views here.
def loginPage(request):
	form = UserCreationForm()

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request,username=username,password=password)

		if user is not None:
			login(request,user)
			return redirect('home')
		else:
			messages.info(request,'Username OR password is incorrect')
	context = {}
	
	return render(request,'accounts/login.html',context)
def logoutUser(request):
	logout(request)
	return redirect('login')
def registerPage(request):
	form = CreateUserForm()
	if request.method == 'POST':
		print(request.POST)
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()

	context = {'form':form}
	return render(request,'accounts/register.html',context)
@login_required(login_url='login')
def home(request):
	customers = Customer.objects.all()
	orders = Order.objects.all()
	total_orders = orders.count()
	orders_pending = orders.filter(status='Pending').count()
	orders_delivered = orders.filter(status='Delivered').count()
	context = {
		'customers':customers,
		'orders':orders,
		'total_orders':total_orders,
		'orders_pending':orders_pending,
		'orders_delivered':orders_delivered,
	}
	return render(request, 'accounts/dashboard.html',context)
@login_required(login_url='login')
def products(request):
	return render(request, 'accounts/products.html')
@login_required(login_url='login')
def customer(request,pk_id):
	customer = Customer.objects.get(id=pk_id)
	orders = customer.order_set.all()
	orders_count = orders.count()
	# myfilter = OrderFilter(request.GET,queryset=orders)
	# orders = myfilter.qs

	context = {
		'customer':customer,
		'orders':orders,
		'orders_count':orders_count,
	}
	return render(request, 'accounts/customer.html',context)
@login_required(login_url='login')
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'),extra=3)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		#print('Printing POST:', request.POST)
		#form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	context = {'form':formset}
	return render(request, 'accounts/order_form.html', context)
@login_required(login_url='login')
def update_order(request,pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST,instance=order)
		if form.is_valid():
			form.save()
			return redirect('/')
	context = {
		'form':form,
	}

	return render(request,'accounts/orderform.html',context)
@login_required(login_url='login')
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('/')

	context = {'item':order}
	return render(request, 'accounts/delete.html', context)