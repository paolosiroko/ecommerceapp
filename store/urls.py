from django.urls import path
from .views import ProductView
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
	path('Login/', views.CustomLoginView.as_view(), name='login'),
    path('Register/', views.RegisterPage.as_view(), name='register'),
	path('logout/', LogoutView.as_view(next_page='store'), name='logout'),
	
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    path('product/<int:pk>/', ProductView.as_view(), name="product")


]
