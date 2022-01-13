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
"hoboken_mid":"E1ZBMYHNCNPW1",
"elizabteh_mid":"9Y0C8GNEMNW61"
}


rutherford_api_token = "2724e5b5-302a-99d2-b78e-8cfd8bba4199"
watchung_api_token = "ad01983e-b3f5-682b-6542-bdee520fa700"
newark_api_token = "352e4275-2219-bdde-a02a-55c2d2f683a2"
uc_api_token = "9703a12d-57ab-d459-e276-2d38a44ce20e"
hoboken_api_token = "0e9fa16c-1b5e-aafe-f7a4-1352b965f78f"
elizabeth_api_token = "bcd3517a-5046-f8b5-7526-9926f2c5ee25"



def cash_request(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }
    response = requests.get(
        url=f"https://api.clover.com/v3/merchants/{mid}/cash_events?filter=timestamp>={time}&filter=timestamp<={time2}",
        params=params, headers=header)

    data = response.json()

    intervals = len(data["elements"])


    data_list = data["elements"]
    payment_totals = 0
    adjustment_totals = 0

    for interval in range(intervals):
        if data_list[interval]["type"] != "ADJUSTMENT":
            total = data_list[interval]["amountChange"]

            payment_totals += total

        else:
            adjustment_total = data_list[interval]["amountChange"]
            adjustment_totals+= adjustment_total



    payment_totals = payment_totals / 100
    adjustment_totals = adjustment_totals / 100

    return [payment_totals,adjustment_totals]

def sales_request(time,time2,mid,token):
    header = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {
        "limit": "1000",
    }
    response = requests.get(url=f"https://api.clover.com/v3/merchants/{mid}/orders?filter=clientCreatedTime>={time}&filter=clientCreatedTime<={time2}&expand=discounts%2ClineItems.discounts%2Cpayments%2ClineItems.modifications",params=params, headers=header)

    data = response.json()





    intervals = len(data["elements"])
    data_list = data["elements"]
    payment_totals = 0
    discount_totals = 0
    tax_totals = 0


    for order in range(intervals):

        total= data_list[order]["total"]/100 #Calculate total on all orders and adds to get our sales number.
        tax = total * .06625
        tax_totals +=tax

        payment_totals += (total - tax)
        order_price = 0
        try:
            line_items_interval = len(data_list[order]["lineItems"]["elements"])
        except KeyError:
            line_items_interval =0



        for num_items in range(line_items_interval):

            line_item_price = 0
            try:
                if "modifications" in data_list[order]["lineItems"]["elements"][num_items]:

                    for number in range(len(data_list[order]["lineItems"]["elements"][num_items]["modifications"]["elements"])):

                        line_item_price = data_list[order]["lineItems"]["elements"][num_items]["price"] / 100
                        line_item_price+= data_list[order]["lineItems"]["elements"][num_items]["modifications"]["elements"][number]["amount"]/100



                else:
                    line_item_price = data_list[order]["lineItems"]["elements"][num_items]["price"]/100
            except KeyError :
                pass




            try:
                line_item_order = data_list[order]["lineItems"]["elements"][num_items]
            except KeyError:
                pass

            order_price += line_item_price




            if "discounts" in line_item_order:
                for interval in range(len(line_item_order["discounts"]["elements"])):
                    try:
                        line_item_percent = line_item_order["discounts"]["elements"][interval]["percentage"]/100
                        discount_totals+= line_item_percent * -line_item_price







                    except KeyError:
                        line_item_amount = line_item_order["discounts"]["elements"][interval]["amount"]/100
                        discount_totals+=line_item_amount




            else:
                pass
        if "discounts" in data_list[order]:

            discounts_order_interval = len(data_list[order]["discounts"]["elements"])

            for discount_interval in range(discounts_order_interval):

                try:
                    discount_amount= data_list[order]["discounts"]["elements"][discount_interval]["amount"]/100
                    discount_totals+=discount_amount





                except KeyError:
                    discount_percent = data_list[order]["discounts"]["elements"][discount_interval]["percentage"]/100
                    discount_totals +=discount_percent * -order_price







    return [payment_totals,discount_totals,tax_totals]


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
yesterday = today - timedelta(days=1)


watchung_amount_collected_without_tips = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[0]
watchung_discounts = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[1]

watchung_cash_sales = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[0]
watchung_adjustment = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)[1]
watchung_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 23:00:00'),mid_dictionary["watchung_mid"],watchung_api_token)

rutherford_amount_collected_without_tips = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[0]
rutherford_discounts = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[1]
rutherford_cash_sales = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[0]
rutherford_adjustment = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)[1]
rutherford_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["rutherford_mid"],rutherford_api_token)

newark_amount_collected_without_tips = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["newark_mid"],newark_api_token)[0]
newark_discounts = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["newark_mid"],newark_api_token)[1]
newark_tax = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["newark_mid"],newark_api_token)[2]

newark_adjustment = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["newark_mid"],newark_api_token)[1]
newark_cash_sales = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["newark_mid"],newark_api_token)[0]
newark_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["newark_mid"],newark_api_token)

hoboken_amount_collected_without_tips = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[0]
hoboken_discounts = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[1]

hoboken_cash_sales = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[0]
hoboken_adjustment = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)[1]
hoboken_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["hoboken_mid"],hoboken_api_token)

uc_amount_collected_without_tips = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["uc_mid"],uc_api_token)[0]
uc_discounts = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["uc_mid"],uc_api_token)[1]
uc_cash_sales = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["uc_mid"],uc_api_token)[0]
uc_adjustment = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["uc_mid"],uc_api_token)[1]
uc_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["uc_mid"],uc_api_token)

elizabeth_discounts = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[1]
elizabeth_amount_collected_without_tips = sales_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[0]
elizabeth_cash_sales = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[0]
elizabeth_adjustment = cash_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)[1]
elizabeth_refunds = refund_request(date_to_timestamp(f'{yesterday} - 00:00:00'),date_to_timestamp(f'{yesterday} - 22:00:00'),mid_dictionary["elizabteh_mid"],elizabeth_api_token)





##### Google Sheets Update


scope = {"https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive	"
}
creds = ServiceAccountCredentials.from_json_keyfile_name("Python Sheets Api.json",scope)
client = gspread.authorize(creds)

newark = client.open("PB Daily Deposit Log 2021").sheet1
i=1
while newark.cell(i,1).value != None:
    print(newark.cell(i,1).value)
    print(newark_amount_collected_without_tips)
    print(newark_tax)
    time.sleep(2)
    i = i + 1
newark.update_cell(i,1,f"{yesterday}")
newark.update_cell(i,2,f"{newark_cash_sales}")
newark.update_cell(i,3,f"{newark_refunds}")
newark.update_cell(i,4,f"{newark_adjustment}")
newark.update_cell(i,6,f"{newark_cash_sales - newark_refunds + newark_adjustment}")
newark.update_cell(i,7,f"{newark_discounts}")


hoboken = client.open("PB Daily Deposit Log 2021").worksheet("Hoboken")
i=1
while hoboken.cell(i,1).value != None:
    print(hoboken.cell(i,1).value)
    time.sleep(2)
    i = i + 1
hoboken.update_cell(i,1,f"{yesterday}")
hoboken.update_cell(i,2,f"{hoboken_cash_sales}")
hoboken.update_cell(i,3,f"{hoboken_refunds}")
hoboken.update_cell(i,4,f"{hoboken_adjustment}")
hoboken.update_cell(i,6,f"{hoboken_cash_sales - hoboken_refunds + hoboken_adjustment}")
hoboken.update_cell(i,7,f"{hoboken_discounts}")

rutherford = client.open("PB Daily Deposit Log 2021").worksheet("Rutherford")
i=1
while rutherford.cell(i,1).value != None:
    print(rutherford.cell(i,1).value)
    time.sleep(1)
    i = i + 1
rutherford.update_cell(i,1,f"{yesterday}")
rutherford.update_cell(i,2,f"{rutherford_cash_sales}")
rutherford.update_cell(i,3,f"{rutherford_refunds}")
rutherford.update_cell(i,4,f"{rutherford_adjustment}")
rutherford.update_cell(i,6,f"{rutherford_cash_sales - rutherford_refunds + rutherford_adjustment}")
rutherford.update_cell(i,7,f"{rutherford_discounts}")

uc = client.open("PB Daily Deposit Log 2021").worksheet("Union City")
i=1
while uc.cell(i,1).value != None:
    print(uc.cell(i,1).value)
    time.sleep(2)
    i = i + 1
uc.update_cell(i,1,f"{yesterday}")
uc.update_cell(i,2,f"{uc_cash_sales}")
uc.update_cell(i,3,f"{uc_refunds}")
uc.update_cell(i,4,f"{uc_adjustment}")
uc.update_cell(i,6,f"{uc_cash_sales - uc_refunds + uc_adjustment}")
uc.update_cell(i,7,f"{uc_discounts}")

watchung = client.open("PB Daily Deposit Log 2021").worksheet("Watchung")
i=1
while watchung.cell(i,1).value != None:
    print(watchung.cell(i,1).value)
    time.sleep(2)
    i = i + 1
watchung.update_cell(i,1,f"{yesterday}")
watchung.update_cell(i,2,f"{watchung_cash_sales}")
watchung.update_cell(i,3,f"{watchung_refunds}")
watchung.update_cell(i,4,f"{watchung_adjustment}")
watchung.update_cell(i,6,f"{watchung_cash_sales - watchung_refunds + watchung_adjustment}")
watchung.update_cell(i,7,f"{watchung_discounts}")


elizabeth = client.open("PB Daily Deposit Log 2021").worksheet("Elizabeth")
i=1
while elizabeth.cell(i,1).value != None:
    print(elizabeth.cell(i,1).value)
    time.sleep(2)
    i = i + 1
elizabeth.update_cell(i,1,f"{yesterday}")
elizabeth.update_cell(i,2,f"{elizabeth_cash_sales}")
elizabeth.update_cell(i,3,f"{elizabeth_refunds}")
elizabeth.update_cell(i,4,f"{elizabeth_adjustment}")
elizabeth.update_cell(i,6,f"{elizabeth_cash_sales - elizabeth_refunds + elizabeth_adjustment}")
elizabeth.update_cell(i,7,f"{elizabeth_discounts}")

print(rutherford_adjustment)
print(uc_adjustment)

if elizabeth_adjustment < -20:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("lamar1102@gmail.com", "Maryland2019")
        connection.sendmail(
            from_addr="lamar1102@gmail.com",
            to_addrs="lamar@playabowlsrun.com",
            msg=f"Subject: PayOut Alert! \n"
            
            f"In the Elizabeth Store on {yesterday} there was ${elizabeth_adjustment} in total payouts!"
        )

if newark_adjustment < -20:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("lamar1102@gmail.com", "Maryland2019")
        connection.sendmail(
            from_addr="lamar1102@gmail.com",
            to_addrs="lamar@playabowlsrun.com",
            msg=f"Subject: PayOut Alert! \n"

                f"In the Newark Store on {yesterday} there was ${newark_adjustment} in total payouts!"
        )

if rutherford_adjustment < -20:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("lamar1102@gmail.com", "Maryland2019")
        connection.sendmail(
            from_addr="lamar1102@gmail.com",
            to_addrs="lamar@playabowlsrun.com",
            msg=f"Subject: PayOut Alert! \n"

                f"In the Rutherford Store on {yesterday} there was ${rutherford_adjustment} in total payouts!"
        )

if watchung_adjustment < -20:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("lamar1102@gmail.com", "Maryland2019")
        connection.sendmail(
            from_addr="lamar1102@gmail.com",
            to_addrs="lamar@playabowlsrun.com",
            msg=f"Subject: PayOut Alert! \n"

                f"In the Watchung Store on {yesterday} there was ${watchung_adjustment} in total payouts!"
        )

if hoboken_adjustment < -20:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("lamar1102@gmail.com", "Maryland2019")
        connection.sendmail(
            from_addr="lamar1102@gmail.com",
            to_addrs="lamar@playabowlsrun.com",
            msg=f"Subject: PayOut Alert! \n"

                f"In the Hoboken Store on {yesterday} there was ${hoboken_adjustment} in total payouts!"
        )

if uc_adjustment < -20:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login("lamar1102@gmail.com", "Maryland2019")
        connection.sendmail(
            from_addr="lamar1102@gmail.com",
            to_addrs="lamar@playabowlsrun.com",
            msg=f"Subject: PayOut Alert! \n"

                f"In the Union City Store on {yesterday} there was ${uc_adjustment} in total payouts!"
        )

print("Successful Run Through")



