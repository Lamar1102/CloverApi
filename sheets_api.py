from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = {"https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive	"
}
creds = ServiceAccountCredentials.from_json_keyfile_name("Python Sheets Api.json",scope)
client = gspread.authorize(creds)

test = client.open("Daily Deposit Log").sheet1

i=1
while test.cell(i,1).value != None:
    print(test.cell(i,1).value)
    i = i + 1

test.update_cell(i,1,f"{yesterday}")
test.update_cell(i,2,f"{watchung_cash_sales}")
test.update_cell(i,3,f"{watchung_refunds}")
test.update_cell(i,6,f"{watchung_cash_sales - watchung_refunds}")

test.update_cell(i,7,f"{watchung_discounts}")

for interval in range(intervals):
    total = data_list[interval]["total"]  # Calculate total on all orders and adds to get our sales number.
    payment_totals += total
    try:
        discount_intervals = len(data_list[interval]["discounts"]["elements"])
    except KeyError:
        pass
    else:
        for discount_interval in range(discount_intervals):
            try:
                discount = data_list[interval]["discounts"]["elements"][discount_interval]["amount"]
                tax = discount * .06625

                discount_totals += discount
                print(discount)

            except KeyError:
                try:
                    discount_percent = data_list[interval]["discounts"]["elements"][discount_interval]["percentage"]
                    order_total = data_list[interval]["total"]
                    discount = -order_total / (((100 - discount_percent) / 100))
                    tax = round((discount * .066624) / 100, 2)

                    discount = discount - (tax / 100)
                    # print(discount)

                    discount_totals += (discount * (discount_percent / 100))
                    # print((discount*(discount_percent/100)))
                    # print(order_total,round(discount/100 , 1))
                    # print(tax,discount)
                except ZeroDivisionError:
                    pass

    try:
        line_intervals = len(data_list[interval]["lineItems"]["elements"])
    except KeyError:
        pass

    for line in range(line_intervals):

        try:

            for num in range(len(data_list[interval]["lineItems"]["elements"][line]["discounts"]["elements"])):
                line_discount = round(
                    data_list[interval]["lineItems"]["elements"][line]["discounts"]["elements"][num]["amount"], 2)
                tax = line_discount * .06625
                discount_totals += line_discount
                # print(line_discount)
        except KeyError:
            pass

        try:

            for num in range(len(data_list[interval]["lineItems"]["elements"][line]["discounts"]["elements"])):
                line_discount_percent = \
                data_list[interval]["lineItems"]["elements"][line]["discounts"]["elements"][num]["percentage"]
                order_total = data_list[interval]["total"]
                line_discount = round((-order_total) / (line_discount_percent / 100), 2)
                tax = line_discount * .06625

                discount_totals += line_discount
                print(line_discount)
        except KeyError:
            pass

return [payment_totals, round(discount_totals, 2)]