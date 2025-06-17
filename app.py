from flask import Flask, render_template, request, redirect, send_file, session, flash, url_for
import csv, os
from datetime import datetime
from collections import defaultdict
import openpyxl
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Thay bằng key ngẫu nhiên nếu dùng thật
bcrypt = Bcrypt(app)

USERNAME = 'admin'
PASSWORD_HASH = bcrypt.generate_password_hash('123456').decode('utf-8')

SALES_FILE = 'sales.csv'


# ======= LOGIN BẢO VỆ =======
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and bcrypt.check_password_hash(PASSWORD_HASH, password):
            session['user'] = username
            return redirect('/')
        else:
            flash('Sai tài khoản hoặc mật khẩu!', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ======= THÊM ĐƠN =======
def save_sale(item, quantity, price):
    try:
        date = datetime.now().strftime('%Y-%m-%d')
        file_exists = os.path.isfile(SALES_FILE)

        if not file_exists:
            with open(SALES_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Item', 'Quantity', 'Price'])

        with open(SALES_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([date, item, quantity, price])
        print(f"✅ Đã ghi: {item} - {quantity} - {price}")

    except Exception as e:
        print("⛔ Lỗi khi ghi file sales.csv:", e)


# ======= XỬ LÝ DỮ LIỆU =======
def get_sales_by_month(month=None):
    sales = []
    daily_totals = defaultdict(float)
    monthly_total = 0.0

    if not os.path.exists(SALES_FILE):
        return sales, monthly_total, daily_totals

    with open(SALES_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                if not row['Date']:
                    continue
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
            except Exception as e:
                print("⛔ Bỏ qua dòng lỗi:", row, "| Lý do:", e)
                continue

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


# ======= ROUTES =======

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        item = request.form['item']
        quantity = request.form['quantity']
        price = request.form['price']
        save_sale(item, quantity, price)
        return redirect('/')
    return render_template('index.html')


@app.route('/report')
@login_required
def report():
    month = request.args.get('month')
    sales, total, chart_data = get_sales_by_month(month)
    return render_template('report.html', sales=sales, total=total, month=month, chart_data=chart_data)


@app.route('/export')
@login_required
def export():
    month = request.args.get('month')
    sales, _, = get_sales_by_month(month)
    filename = export_to_excel(month, sales)
    return send_file(filename, as_attachment=True)


# ======= CHẠY APP =======
if __name__ == '__main__':
    app.run(debug=True)
