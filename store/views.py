from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart,cartData,guestOrder

from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login


class CustomLoginView(LoginView):
    template_name = 'store/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('store')

class RegisterPage(FormView):
    template_name = 'store/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('store')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('store')
        return super(RegisterPage, self).get(*args, **kwargs)


def store(request):
	data = cartData(request)
	cartItems = data['cartItems']

	products = Product.objects.all()
	context = {
		'products': products,
		'cartItems': cartItems,
	}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items': items,
		'order': order,
		'cartItems': cartItems,
	}
	return render(request, 'store/cart.html', context)


def checkout(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {
		'items': items,
		'order': order,
		'cartItems': cartItems,
	}
	return render(request, 'store/checkout.html', context)


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

	else:
		customer, order = guestOrder(request, data)

		total = float(data['form']['total'])
		order.transaction_id = transaction_id

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		if order.shipping == True:
			ShippingAddress.objects.create(
				customer=customer,
				order = order,
				address = data["shipping"]["address"],
				city= data["shipping"]["city"],
				state = data["shipping"]["state"],
				zipcode = data["shipping"]["zipcode"]
			)

		else:
			print("user not logged in")

	return JsonResponse('Payment submitted..', safe=False)

class ProductView (DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'store/product.html'




