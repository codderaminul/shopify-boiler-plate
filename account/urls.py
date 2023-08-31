from django.urls import path
from account import views
app_name = "account"

urlpatterns = [
    path('', views.account,name="account"), 
    path('authenticate/', views.authenticate,name="authenticate"),
    path('finalize/', views.finalize,name="finalize"),
    path('logout/', views.logout,name="logout"),
    path('webhooks/customers/data_request/', views.data_request_webhook, name='data_request_webhook'),
    path('webhooks/customers/redact/', views.redact_webhook, name='redact_webhook'),
    path('webhooks/shop/redact/', views.shop_react_webhook, name='shop_react_webhook'),
    # Billing API
    path('create-subscription/', views.create_one_time_purchase, name='create-subscription'),
    path('invoice-page', views.invoice_page, name='invoice_page'),
]