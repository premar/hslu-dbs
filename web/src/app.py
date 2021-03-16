from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

QUERY = """
SELECT products.productName AS Product,
       SUM(orderdetails.quantityOrdered) as Quantity,
       SUM((orderdetails.quantityOrdered * products.buyPrice)) as Cost,
       SUM((orderdetails.quantityOrdered * orderdetails.priceEach)) as Sell,
       SUM((orderdetails.quantityOrdered * products.MSRP)) as Retail,
       SUM((orderdetails.quantityOrdered * orderdetails.priceEach) - (orderdetails.quantityOrdered * products.buyPrice)) AS Profit
from orders
    left join orderdetails on orders.orderNumber = orderdetails.orderNumber
    left join products on products.productCode = orderdetails.productCode
WHERE orders.orderDate BETWEEN date('2003-01-01') AND date('2005-12-31')
GROUP BY products.productCode
ORDER BY Profit DESC;
"""

@app.route('/')
def server():
    product = []
    quantity = []
    cost = []
    sell = []
    retail = []
    profit = []

    connection = mysql.connector.connect(
        user='',
        password='',
        host='dbs-f21-mpreuss.enterpriselab.ch',
        database='classicmodels',
        port=8080)

    with connection.cursor() as cursor:
        cursor.execute(QUERY)
        result = cursor.fetchall()
        for row in result:
            product.append(row[0])
            quantity.append(row[1])
            cost.append(row[2])
            sell.append(row[3])
            retail.append(row[4])
            profit.append(row[5])
    return render_template('index.html', labels=product, values=profit, title="DBS")


if __name__ == '__main__':
    app.run()
