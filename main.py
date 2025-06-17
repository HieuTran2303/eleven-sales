import csv
import os
from datetime import datetime
from collections import defaultdict
import openpyxl

SALES_FILE = 'sales.csv'

def add_sale(item, quantity, price):
    date = datetime.now().strftime("%Y-%m-%d")
    sale = [date, item, quantity, price]
    file_exists = os.path.isfile(SALES_FILE)

    with open(SALES_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Item', 'Quantity', 'Price'])
        writer.writerow(sale)
    print("✅ Sale recorded!")

def monthly_report(filtered_month=None):
    if not os.path.isfile(SALES_FILE):
        print("⚠️ No sales data found.")
        return

    monthly_totals = defaultdict(float)
    sales_data = []

    with open(SALES_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = datetime.strptime(row['Date'], "%Y-%m-%d")
            total = float(row['Price']) * int(row['Quantity'])
            month_str = date.strftime("%Y-%m")
            monthly_totals[month_str] += total

            if not filtered_month or month_str == filtered_month:
                sales_data.append([
                    row['Date'],
                    row['Item'],
                    row['Quantity'],
                    row['Price'],
                    f"{total:.2f}"
                ])

    if filtered_month:
        print(f"\n📆 Sales Report for {filtered_month}:")
        for sale in sales_data:
            print(" | ".join(sale))
        print(f"🧾 Total: ${monthly_totals[filtered_month]:.2f}")
        export_to_excel(filtered_month, sales_data)
    else:
        print("\n📊 Full Monthly Sales Summary:")
        for month, total in sorted(monthly_totals.items()):
            print(f"{month}: ${total:.2f}")

def export_to_excel(month, data):
    filename = f"sales_report_{month}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Monthly Report"

    headers = ['Date', 'Item', 'Quantity', 'Price', 'Total']
    ws.append(headers)

    for row in data:
        ws.append(row)

    wb.save(filename)
    print(f"📁 Excel report saved as: {filename}")

def main():
    while True:
        print("\n=== ElEvEn Sales App ===")
        print("1. Add New Sale")
        print("2. View Monthly Report")
        print("3. View All Monthly Totals")
        print("4. Exit")
        choice = input("👉 Choose (1/2/3/4): ")

        if choice == '1':
            item = input("Item name: ")
            quantity = int(input("Quantity: "))
            price = float(input("Price per item: "))
            add_sale(item, quantity, price)

        elif choice == '2':
            month = input("Enter month to view (YYYY-MM): ")
            monthly_report(filtered_month=month)

        elif choice == '3':
            monthly_report()

        elif choice == '4':
            print("👋 Later, legend!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
