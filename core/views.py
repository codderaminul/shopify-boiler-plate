from account.decorators import shop_login_required
from django.shortcuts import render
import shopify
from django.core.paginator import Paginator


global page_number
page_number = '1'
@shop_login_required
def index(request):
    global page_number
    shop = shopify.Shop.current()
  
    max = 200
    for attampt in range(max):
        try:
            products = shopify.Product.find()
            paginator = Paginator(products, 5)  
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print('find')
            break
        except Exception as e:
            print(e)
            print('something wrong')
            if attampt == max - 1:
                page_obj = ''
            continue
    context = {
        'shop_id':shop.id,
        'page_obj':page_obj,
    }
    return render(request, 'home/index.html',context)


