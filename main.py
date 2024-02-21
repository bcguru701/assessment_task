from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from django.conf import settings
import django
import os
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assesment_task.settings")
django.setup()

from task.models import Currency

app = FastAPI()

class CurrencyUpdateResponse(BaseModel):
    message: str
    last_update_date: str

class LastUpdateResponse(BaseModel):
    last_update_date: str

class ConversionResponse(BaseModel):
    amount: float

class CurrencyConversionRequest(BaseModel):
    source_currency_code: str
    target_currency_code: str
    amount_to_convert: Decimal


@app.put("/update-exchange-rates/")
def update_exchange_rates():
    response = requests.get('https://open.er-api.com/v6/latest')
    data = response.json()

    if response.status_code == 200:
        for code, rate in data['rates'].items():
            currency, created = Currency.objects.get_or_create(code=code)
            currency.name = code
            currency.rate = rate
            currency.save()

        return CurrencyUpdateResponse(
            message="Exchange rates fetched and saved successfully.",
            last_update_date=data['time_last_update_utc']
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch exchange rates")


@app.get("/last-update-time/")
def get_last_update_time():
    last_update = Currency.objects.latest('id')
    return LastUpdateResponse(last_update_date=last_update.created_at.strftime('%Y-%m-%d %H:%M:%S'))


@app.post("/convert-currency/")
def convert_currency(request_data: CurrencyConversionRequest):
    try:
        source_currency = Currency.objects.get(code=request_data.source_currency_code)
        target_currency = Currency.objects.get(code=request_data.target_currency_code)

        if source_currency.rate is None or target_currency.rate is None:
            raise HTTPException(status_code=400, detail="Exchange rates not available for specified currencies")

        conversion_result = (float(request_data.amount_to_convert) / float(source_currency.rate)) * float(target_currency.rate)
        return ConversionResponse(amount=conversion_result)

    except Currency.DoesNotExist:
        raise HTTPException(status_code=400, detail="One or both currencies not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid input")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
