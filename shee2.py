import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

import requests
import datetime
from datetime import timedelta
import time

import smtplib
import time


mid_dictionary = {
"watchung_mid":"5VHZX7YQ845H1",
"uc_mid":"RZVGWVQESBGH1",
"newark_mid":"QZNR169QX96Q1",
"rutherford_mid":"315ZB443CPFA1",
"hoboken_mid":"ES5KMD7WWK034",
"elizabteh_mid":"9Y0C8GNEMNW61"
}


rutherford_api_token = "2724e5b5-302a-99d2-b78e-8cfd8bba4199"
watchung_api_token = "ad01983e-b3f5-682b-6542-bdee520fa700"
newark_api_token = "352e4275-2219-bdde-a02a-55c2d2f683a2"
uc_api_token = "9703a12d-57ab-d459-e276-2d38a44ce20e"
hoboken_api_token = "3935c08f-b1a9-603c-d561-cee302842a6f"
elizabeth_api_token = "bcd3517a-5046-f8b5-7526-9926f2c5ee25"

def sales_request(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }
    response = requests.get(url=f"https://api.clover.com/v3/merchants/{mid}/orders?filter=clientCreatedTime>={time}&filter=clientCreatedTime<={time2}&expand=discounts%2ClineItems.discounts%2CtipAmount%2Cpayments%2ClineItems.modifications",params=params, headers=header)

    data = response.json()




    intervals = len(data["elements"])

    data_list = data["elements"]
    payment_totals = 0

    for order in range(intervals):
        total = data_list[order]["total"] / 100  # Calculate total on all orders and adds to get our sales number.
        tax = total * .063

        payment_totals += (total - tax)


    return (payment_totals)

def tips(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }
    response = requests.get(
        url=f"https://api.clover.com/v3/merchants/{mid}/payments?filter=clientCreatedTime>={time}&filter=clientCreatedTime<={time2}&expand=lineItemPayments%2Cpayments%2CcardTransactions%2CtransactionInfo%2CdccInfo",
        params=params, headers=header)

    data = response.json()




    intervals = len(data["elements"])
    print(intervals)

    data_list = data["elements"]

    tips = 0
    tax=0
    net_sales = 0

    for order in range(intervals):
        try:
            amount = data_list[order]["tipAmount"]/100
        except KeyError:
            amount=0

        tax_amount = data_list[order]["taxAmount"]/100
        sales= data_list[order]["amount"]/100
        tips+=amount
        tax+=tax_amount
        net_sales+=sales-tax_amount


    return [tips,tax,net_sales]

def refund_request(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }
    response = requests.get(url=f"https://api.clover.com/v3/merchants/{mid}/refunds?filter=clientCreatedTime>={time}&filter=clientCreatedTime<={time2}",params=params, headers=header)

    data = response.json()


    intervals = len(data["elements"])

    data_list = data["elements"]


    tax = 0
    refund_total = 0

    for order in range(intervals):

        tax_amount = data_list[order]["taxAmount"] / 100
        refund = data_list[order]["amount"] / 100

        tax += tax_amount
        refund_total += refund - tax_amount

    return [refund_total,tax]

def credit_refund(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }

    response = requests.get(
        url=f"https://api.clover.com/v3/merchants/{mid}/credit_refunds?filter=clientCreatedTime>={time}&filter=clientCreatedTime<={time2}",
        params=params, headers=header)

    data = response.json()


def date_to_timestamp(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d - %H:%M:%S")
    date = datetime.datetime.timestamp(date)
    # print(round(date*1000))
    return round(date*1000)


today = datetime.date.today()

yesterday = today - timedelta(days=1)
last_week = today - timedelta(days=7)
last_month = today - timedelta(days=30)
last_year = today - timedelta(days=365)




watchung_sales=tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[2]
watchung_tips = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[0]
watchung_tax = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[1]
watchung_refunds=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[0]
watchung_refunds_tax=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[1]
watchung_sales = watchung_sales-watchung_refunds
watchung_tax =watchung_tax-watchung_refunds_tax

hoboken_sales=tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[2]
hoboken_tips = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[0]
hoboken_tax = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[1]
hoboken_refunds=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[0]
hoboken_refunds_tax=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[1]
hoboken_sales = hoboken_sales-hoboken_refunds
hoboken_tax =hoboken_tax-hoboken_refunds_tax

uc_sales=tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["uc_mid"],uc_api_token)[2]
uc_tips = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["uc_mid"],uc_api_token)[0]
uc_tax = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["uc_mid"],uc_api_token)[1]
uc_refunds=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["uc_mid"],uc_api_token)[0]
uc_refunds_tax=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["uc_mid"],uc_api_token)[1]
uc_sales = uc_sales-uc_refunds
uc_tax =uc_tax-uc_refunds_tax

time.sleep(1)

rutherford_sales=tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[2]
rutherford_tips = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[0]
rutherford_tax = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[1]
rutherford_refunds=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[0]
rutherford_refunds_tax=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[1]
rutherford_sales = rutherford_sales-rutherford_refunds
rutherford_tax =rutherford_tax-rutherford_refunds_tax

elizabeth_sales=tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[2]
elizabeth_tips = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[0]
elizabeth_tax = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[1]
elizabeth_refunds=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[0]
elizabeth_refunds_tax=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[1]
elizabeth_tax =elizabeth_tax-elizabeth_refunds_tax
elizabeth_sales = elizabeth_sales-elizabeth_refunds-elizabeth_tax


newark_sales=tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["newark_mid"],newark_api_token)[2]
newark_tips = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["newark_mid"],newark_api_token)[0]
newark_tax = tips(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["newark_mid"],newark_api_token)[1]
newark_refunds=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["newark_mid"],newark_api_token)[0]
newark_refunds_tax=refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["newark_mid"],newark_api_token)[1]
newark_sales = newark_sales-newark_refunds
newark_tax =newark_tax-newark_refunds_tax

x = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)
print(hoboken_sales)
print(hoboken_tips)
print(hoboken_tax)

print(uc_sales)
print(uc_tips)
print(uc_tax)

print(rutherford_sales)
print(rutherford_refunds)
print(rutherford_tips)
print(rutherford_tax)

print(newark_sales)
print(newark_refunds)
print(newark_tips)
print(newark_tax)

print(watchung_sales)
print(watchung_tips)
print(watchung_tax)

print(elizabeth_sales)
print(elizabeth_tips)
print(elizabeth_tax)




