import datetime
import math
from flask import Flask, render_template, jsonify
import mysql.connector

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('config.py')

DEFAULT_START_DATE = '2003-01-01'
DEFAULT_END_DATE = '2005-12-31'
DEFAULT_INDEX = 'TotalProfit'
VALID_INDEX = ("Product", "Quantity", "currentStorageQuantity", "Cost", "AvgSellPrice", "AvgProfit", "PossibleProfit", "ProfitDifference", "TotalProfit")

QUERY = """
SELECT p.productName as Product,
       p.buyPrice as Cost,
	   p.MSRP as MSRP,
       p.quantityInStock as currentStorageQuantity,
       AVG(od.priceEach) as AvgSellPrice,
       AVG(od.priceEach - p.buyPrice) AS AvgProfit,
       SUM(od.quantityOrdered) as Quantity,
       SUM((od.quantityOrdered * od.priceEach) - (od.quantityOrdered * p.buyPrice)) AS TotalProfit,
       SUM((od.quantityOrdered * p.MSRP) - (od.quantityOrdered * p.buyPrice)) AS PossibleProfit,
       SUM(
		(od.quantityOrdered * p.MSRP) - (od.quantityOrdered * p.buyPrice) - (
			(od.quantityOrdered * od.priceEach) - (od.quantityOrdered * p.buyPrice)
		)
       ) AS ProfitDifference
from orders o
    left join orderdetails od on o.orderNumber = od.orderNumber
    left join products p on p.productCode = od.productCode
WHERE o.orderDate BETWEEN %s AND %s
GROUP BY p.productCode
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
    cost = []
    msrp = []
    storage_quantity = []
    avg_sell_price = []
    avg_profit = []
    quantity = []
    actual_profit = []
    possible_profit = []
    profit_differnece = []
    

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
            cost.append(math.trunc(row[1]))
            msrp.append(math.trunc(row[2]))
            storage_quantity.append(math.trunc(row[3]))
            avg_sell_price.append(math.trunc(row[4]))
            avg_profit.append(math.trunc(row[5]))
            quantity.append(math.trunc(row[6]))
            actual_profit.append(math.trunc(row[7]))
            possible_profit.append(math.trunc(row[8]))
            profit_differnece.append(math.trunc(row[9]))

    data = (
        ("Buy price in [$]", "#EB0800", cost),
        ("MSRP in [$]", "#14FFC1", msrp),
        ("Quantity in storage as [Qty]", "#E87935", storage_quantity),
        ("Average sell price in [$]", "#3886F2", avg_sell_price),
        ("Average profit in [$]", "#588C50", avg_profit),
        ("Quantity sold as [Qty]", "#ffa600", quantity),
        ("Total profit in [$]", "#58508d", actual_profit),
        ("Possible profit in [$]", "#bc5090", possible_profit),
        ("Difference of possible to actual profit in [$]", "#ff6361", profit_differnece),
    )
    return data, product


def bad_request():
    resp = jsonify("400 Bad Request")
    resp.status_code = 400
    return resp


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)
