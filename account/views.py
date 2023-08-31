from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.apps import apps
from urllib.parse import parse_qs, urlparse
import requests
import shopify
from django.views.decorators.csrf import csrf_exempt
from account.models import Plan
import hmac, base64, hashlib, binascii, os
from urllib.parse import parse_qs, urlparse
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from account.decorators import shop_login_required



def _new_session(shop_url):
    api_version = apps.get_app_config('account').SHOPIFY_API_VERSION
    return shopify.Session(shop_url, api_version) 

def authenticate(request):
    url = request.get_full_path()
    print('url',url)
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    try:
        shop_url = query_params.get('shop')[0]
        # add shop_url to session
        request.session['shop_url'] = shop_url
    except:
        # get shop_url from session
        shop_url = request.session.get('shop_url')

    if shop_url == None:
        return render(request,'home/None.html')
    
    scope = apps.get_app_config('account').SHOPIFY_API_SCOPE
    redirect_uri = request.build_absolute_uri(reverse('account:finalize'))
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    request.session['shopify_oauth_state_param'] = state
    permission_url = _new_session(shop_url).create_permission_url(scope, redirect_uri, state)
    return redirect(permission_url)

def finalize(request):
    api_secret = apps.get_app_config('account').SHOPIFY_API_SECRET
    params = request.GET.dict()
    if request.session.get('shopify_oauth_state_param') != params['state']:
        messages.error(request, 'Anti-forgery state token does not match the initial request.')
        return redirect(reverse('account:authenticate'))
    else:
        request.session.pop('shopify_oauth_state_param', None)
    myhmac = params.pop('hmac')
    line = '&'.join([
        '%s=%s' % (key, value)
        for key, value in sorted(params.items())
    ])
    h = hmac.new(api_secret.encode('utf-8'), line.encode('utf-8'), hashlib.sha256)
    if hmac.compare_digest(h.hexdigest(), myhmac) == False:
        messages.error(request, "Could not verify a secure login")
        return redirect(reverse('account:authenticate'))

    try:
        shop_url = params['shop']
        session = _new_session(shop_url)
        request.session['shopify'] = {
            "shop_url": shop_url,
            "access_token": session.request_token(request.GET)
        }
    except Exception:
        messages.error(request, "Could not log in to Shopify store.")
        return redirect(reverse('account:authenticate'))
    
    messages.info(request, "Logged in to shopify store.")
    request.session.pop('return_to', None)
    return redirect(request.session.get('return_to', reverse('core:index')))

def verify_webhook(data, hmac_header):
    api_secret = apps.get_app_config('core').SHOPIFY_API_SECRET
    digest = hmac.new(api_secret.encode('utf-8'), data, digestmod=hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

@csrf_exempt
def data_request_webhook(request):
    if request.method == 'POST':
        data = request.body  # Request body contains the JSON payload
        verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verified:
            return HttpResponse(status=401)  # Unauthorized
        return HttpResponse(status=200)  # Response success
    return HttpResponse(status=405)  # Method Not Allowed if not a POST request

# customers/redact webhook
@csrf_exempt
def redact_webhook(request):
    if request.method == 'POST':
        data = request.body  # Request body contains the JSON payload
        verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verified:
            return HttpResponse(status=401)  # Unauthorized
        return HttpResponse(status=200)  # Response success
    return HttpResponse(status=405)  # Method Not Allowed if not a POST request

# shop/react webhook 
@csrf_exempt
def shop_react_webhook(request):
    if request.method == 'POST':
        data = request.body  # Request body contains the JSON payload
        verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
        if not verified:
            return HttpResponse(status=401)  # Unauthorized
        return HttpResponse(status=200)  # Response success
    return HttpResponse(status=405)  # Method Not Allowed if not a POST request

def logout(request):
    request.session.pop('shopify', None)
    messages.info(request, "Successfully logged out.")
    return redirect(reverse('account:authenticate'))


@csrf_exempt
@shop_login_required
def account(request):
    plans = Plan.objects.all()
    return render(request,'home/account.html',{'plans':plans})

def invoice_page(request):
    print('start here')
    price = request.GET.get('price')
    image_num = request.GET.get('image_num')
    data_level = request.GET.get('data_level')
    stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY
    context = {
        'data_level': data_level,
        'total_amount': price,
        'stripe_public_key': stripe_public_key,
        'total_image': image_num,
    }
    return render(request, 'home/invoice.html', context)


# Billing API
def create_one_time_purchase(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        data_level = request.POST.get('data_level')
        price = request.POST.get('price')
        image_num = request.POST.get('image')
        shop_url = request.session.get('shop_url')
    
        shop_domain = request.session.get('shop_url')
        api_version = "2023-04"  # Update this with the correct version
        url = f"https://{shop_domain}/admin/api/{api_version}/graphql.json"

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": request.session['shopify']['access_token'],  # Replace with your access token
        }

        data = {
            "query": """
            mutation {
                appPurchaseOneTimeCreate(
                    name: "Background Image Remover"
                    price: { amount: %s, currencyCode: USD }
                    returnUrl: "http://super-duper.shopifyapps.com"
                ) {
                    userErrors {
                        field
                        message
                    }
                    confirmationUrl
                    appPurchaseOneTime {
                        id
                    }
                }
            }
            """%price
        }

        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        # Handle the response data
        confirmation_url = response_json["data"]["appPurchaseOneTimeCreate"]["confirmationUrl"]
        return JsonResponse({'url':str(confirmation_url)}, status=200)

