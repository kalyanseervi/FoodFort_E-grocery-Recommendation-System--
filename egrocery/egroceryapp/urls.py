from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_results/', views.search_results, name='search_results'),
    path('search_results_suggestion/', views.search_results_suggestion, name='search_results_suggestion'),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('suggestion/', views.suggestion, name='suggestion'),
    path('myaccount/', views.myaccount, name='myaccount'),
    path('order_history/', views.order_history, name='order_history'),
    path('login/', views.loginform, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.sign_out, name='logout'),
    path('shop/', views.shop, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('cart/', views.cart, name='cart'),
    path('payment/', views.initiate_payment, name='payment'),

    path('single_product/<int:Product_detail_id>', views.single_product, name='single_product'),
    path('add_to_cart_dbs/<int:productID>/', views.add_to_cart_dbs, name='add_to_cart_dbs'),
    path("initiate-payment/", views.initiate_payment, name="initiate_payment"),
    path("payment_success/", views.payment_success, name="payment_success"),
    path("payment_failed/", views.payment_failed, name="payment_failed"),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('delete_cart_item/', views.delete_cart_item, name='delete_cart_item'),
    path('get_cart_data/', views.get_cart_data, name='get_cart_data'),
    path('handle-successful-purchase/', views.handle_successful_purchase, name='handle_successful_purchase'),

    
]