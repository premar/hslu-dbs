import math
from flask import Flask, render_template
import mysql.connector

application = Flask(__name__, instance_relative_config=True)
application.config.from_pyfile('config.py')

DEFAULT_START_DATE = '2003-01-01'
DEFAULT_END_DATE = '2005-12-31'

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
WHERE orders.orderDate BETWEEN date('""" + DEFAULT_START_DATE + """') AND date('""" + DEFAULT_END_DATE + """"')
GROUP BY products.productCode
ORDER BY Profit DESC
"""


@application.route('/')
def server():
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
        cursor.execute(QUERY)
        result = cursor.fetchall()
        for row in result:
            product.append(row[0])
            quantity.append(math.trunc(row[1]))
            cost.append(math.trunc(row[2]))
            sell.append(math.trunc(row[3]))
            retail.append(math.trunc(row[4]))
            profit.append(math.trunc(row[5]))

    data = (profit, cost, sell, retail, quantity)

    labels = {
        "Profit",
        "Cost",
        "Sell",
        "Retail",
        "Quantity"
    }

    colors = {
        "Blue",
        "Red",
        "Green",
        "Yellow",
        "Purple"
    }

    return render_template('index.html',
                           label_main=product,
                           values=data,
                           label_sub=labels,
                           label_color=colors,
                           title="DBS")


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=80)
