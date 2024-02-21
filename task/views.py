import json

from django.shortcuts import render
from django.http import JsonResponse
import requests
from .models import Currency
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

def fetch_and_save_exchange_rates(request):
    response = requests.get('https://open.er-api.com/v6/latest')
    data = response.json()

    if response.status_code == 200:
        for code, rate in data['rates'].items():
            currency, created = Currency.objects.get_or_create(code=code)
            currency.name = code
            if rate is not None:
                currency.rate = rate
                currency.save()
            else:
                currency.rate = 0
                currency.save()
        return JsonResponse({'message': 'Exchange rates fetched and saved successfully.', 'last_update_date': data['time_last_update_utc'] })
    else:
        return None

def get_last_update_time(request):
    last_update = Currency.objects.latest('id')
    return JsonResponse({'last_update_date': last_update.created_at.strftime('%Y-%m-%d %H:%M:%S')})


@csrf_exempt
def convert_currency(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            source_currency_code = data.get('source_currency_code', '').upper()
            target_currency_code = data.get('target_currency_code', '').upper()
            amount_to_convert = float(data.get('amount_to_convert', 0))
            source_currency = Currency.objects.get(code=source_currency_code)
            target_currency = Currency.objects.get(code=target_currency_code)
            if source_currency.rate is not None and target_currency.rate is not None:
                conversion_result = (amount_to_convert / float(source_currency.rate)) * float(target_currency.rate)
                return JsonResponse({'conversion_result': conversion_result})
            else:
                return JsonResponse({'error': 'Exchange rates not available for specified currencies'}, status=400)
    except Currency.DoesNotExist:
        return JsonResponse({'error': 'One or both currencies not found'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid input'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)
