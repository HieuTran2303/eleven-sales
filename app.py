from flask import Flask, render_template, request, redirect, send_file
import csv, os
from datetime import datetime
from collections import defaultdict
import openpyxl

app = Flask(__name__)
SALES_FILE = 'sales.csv'

def save_sale(item, quantity, price):
    date = datetime.now().strftime('%Y-%m-%d')
    file_exists = os.path.isfile(SALES_FILE)
    with open(SALES_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Item', 'Quantity', 'Price'])
        writer.writerow([date, item, quantity, price])

def get_sales_by_month(month=None):
    sales = []
    daily_totals = defaultdict(float)
    monthly_total = 0.0

    if not os.path.exists(SALES_FILE):
        return sales, monthly_total, daily_totals

    with open(SALES_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row_date = datetime.strptime(row['Date'], "%Y-%m-%d")
            row_month = row_date.strftime("%Y-%m")
            total = int(row['Quantity']) * float(row['Price'])

            if not month or row_month == month:
                date_str = row_date.strftime("%Y-%m-%d")
                daily_totals[date_str] += total
                monthly_total += total
                sales.append({
                    'date': row['Date'],
                    'item': row['Item'],
                    'quantity': row['Quantity'],
                    'price': row['Price'],
                    'total': f"{total:.2f}"
                })

    return sales, monthly_total, dict(sorted(daily_totals.items()))

def export_to_excel(month, sales):
    filename = f"sales_report_{month}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Report"

    ws.append(['Date', 'Item', 'Quantity', 'Price', 'Total'])

    for s in sales:
        ws.append([s['date'], s['item'], s['quantity'], s['price'], s['total']])

    wb.save(filename)
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form['item']
        quantity = request.form['quantity']
        price = request.form['price']
        save_sale(item, quantity, price)
        return redirect('/')
    return render_template('index.html')

@app.route('/report', methods=['GET'])
def report():
    month = request.args.get('month')
    sales, total, chart_data = get_sales_by_month(month)
    return render_template('report.html', sales=sales, total=total, month=month, chart_data=chart_data)

@app.route('/export', methods=['GET'])
def export():
    month = request.args.get('month')
    sales, _ = get_sales_by_month(month)
    filename = export_to_excel(month, sales)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
