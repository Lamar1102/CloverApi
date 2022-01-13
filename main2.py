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
}


rutherford_api_token = "2724e5b5-302a-99d2-b78e-8cfd8bba4199"
watchung_api_token = "ad01983e-b3f5-682b-6542-bdee520fa700"
newark_api_token = "352e4275-2219-bdde-a02a-55c2d2f683a2"
uc_api_token = "9703a12d-57ab-d459-e276-2d38a44ce20e"
hoboken_api_token = "3935c08f-b1a9-603c-d561-cee302842a6f"

def refund_request(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }
    response = requests.get(url=f"https://api.clover.com/v3/merchants/{mid}/refunds?filter=clientCreatedTime>={time}&filter=clientCreatedTime<={time2}",params=params, headers=header)

    data = response.text
    print(data)

    intervals = len(data["elements"])

    data_list = data["elements"]
    refund_totals = 0

    for interval in range(intervals):
        try:
            total=  data_list[interval]["total"]
            refund_totals += total
        except KeyError:
            pass


    refund_totals = refund_totals / 100

    intervals = len(data["elements"])

    return(refund_totals)


def date_to_timestamp(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d - %H:%M:%S")
    date = datetime.datetime.timestamp(date)
    # print(round(date*1000))
    return round(date*1000)




today = datetime.date.today()
yesterday = today - timedelta(days=4)
print(yesterday)


watchung_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)

print(watchung_refunds)