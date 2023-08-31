from django.apps import AppConfig

class ShopifyAppConfig(AppConfig):
    name = 'account'
    #  easy app
    SHOPIFY_API_KEY= 'c9dbb95de94ebcbb22b6d8a9774677c0'
    SHOPIFY_API_SECRET= 'd6c130e55cff4bba4f05949709156968'
    SHOPIFY_API_VERSION = '2023-04'
    SHOPIFY_API_SCOPE = ['read_products','read_orders','write_products','read_content','write_content','write_files']