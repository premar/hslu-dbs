import datetime
import math
from flask import Flask, render_template, jsonify
import mysql.connector

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('config.py')

DEFAULT_START_DATE = '2003-01-01'
DEFAULT_END_DATE = '2005-12-31'
DEFAULT_INDEX = 'Profit'
VALID_INDEX = ("Quantity", "Cost", "Sell", "Retail", "Profit")

QUERY = """
SELECT products.productName AS Product,
       SUM(orderdetails.quantityOrdered) as Quantity,
       SUM((orderdetails.quantityOrdered * products.buyPrice)) as Cost,
       SUM((orderdetails.quantityOrdered * orderdetails.priceEach)) as Sell,
       SUM((orderdetails.quantityOrdered * products.MSRP)) as Retail,
       SUM((orderdetails.quantityOrdered * orderdetails.priceEach) - 
       (orderdetails.quantityOrdered * products.buyPrice)) AS Profit
from orders
    left join orderdetails on orders.orderNumber = orderdetails.orderNumber
    left join products on products.productCode = orderdetails.productCode
WHERE orders.orderDate BETWEEN %s AND %s
GROUP BY products.productCode
ORDER BY {table} DESC
"""


@application.route('/')
def default():
    data, product = receive_data(DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_INDEX)
    return render_template('index.html', label=product, values=data, title="DBS")


@application.route('/<string:start>/<string:end>/<string:index>')
def custom(start, end, index):
    try:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    except (ValueError, TypeError):
        return bad_request()
    if (start_date < datetime.datetime.strptime(DEFAULT_START_DATE, '%Y-%m-%d') or
            end_date > datetime.datetime.strptime(DEFAULT_END_DATE, '%Y-%m-%d') or
            start_date > end_date):
        return bad_request()
    if index not in VALID_INDEX:
        return bad_request()
    data, product = receive_data(start, end, index)
    return render_template('index.html', label=product, values=data, title="DBS")


def receive_data(start_date, end_date, index):
    product = []
    quantity = []
    cost = []
    sell = []
    retail = []
    profit = []

    connection = mysql.connector.connect(
        user=application.config["USER"],
        password=application.config["PASSWORD"],
        host=application.config["HOST"],
        database=application.config["DATABASE"],
        port=application.config["PORT"])

    with connection.cursor() as cursor:
        cursor.execute(QUERY.format(table=index), (start_date, end_date))
        result = cursor.fetchall()
        for row in result:
            product.append(row[0])
            quantity.append(math.trunc(row[1]))
            cost.append(math.trunc(row[2]))
            sell.append(math.trunc(row[3]))
            retail.append(math.trunc(row[4]))
            profit.append(math.trunc(row[5]))

    data = (
        ("Profit in [$]", "#003f5c", profit),
        ("Cost in [$]", "#58508d", cost),
        ("Sell in  [$]", "#bc5090", sell),
        ("Retail in  [$]", "#ff6361", retail),
        ("Quantity as [Qty]", "#ffa600", quantity),

    )
    return data, product


def bad_request():
    resp = jsonify("400 Bad Request")
    resp.status_code = 400
    return resp


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
