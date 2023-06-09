import mysql.connector
from flask import Flask, render_template
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

app = Flask(__name__)

@app.route('/')
def index():
    # 连接到MySQL数据库
    cnx = mysql.connector.connect(user='root', password='1234',
                                  host='localhost', database='massage')

    # 创建游标对象
    cursor = cnx.cursor()

# 执行查询获取Q4的总价格
    query_q4 = "SELECT SUM(totalPrice) FROM `order` WHERE semester='Q4'"
    cursor.execute(query_q4)
    result_q4 = cursor.fetchone()
    total_price_q4 = result_q4[0] if result_q4 else 0

    # 执行查询获取Q3的总价格
    query_q3 = "SELECT SUM(totalPrice) FROM `order` WHERE semester='Q3'"
    cursor.execute(query_q3)
    result_q3 = cursor.fetchone()
    total_price_q3 = result_q3[0] if result_q3 else 0

    # 计算百分比差异
    percentage_change = ((total_price_q4 - total_price_q3) / total_price_q3) * 100 if total_price_q3 != 0 else 0

    percentage_change=round(percentage_change, 1)

    # 执行查询获取总价格
    query_total = "SELECT SUM(totalPrice) FROM `order` WHERE semester='Q4'"
    cursor.execute(query_total)
    result_total = cursor.fetchone()
    total_price = result_total[0] if result_total else 0

    # 执行查询获取其他数据
    query_data = "SELECT semester, salesmanId, SUM(orderNum) FROM `order` GROUP BY semester, salesmanId"
    cursor.execute(query_data)
    results = cursor.fetchall()

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()

    # 创建字典来存储数据
    data = {}

    # 遍历查询结果
    for row in results:
        semester = row[0]
        salesman_id = row[1]
        order_num = row[2]

        # 如果字典中没有该学期的键，则创建新键
        if semester not in data:
            data[semester] = {}

        # 如果字典中没有该学期、业务员ID的键，则创建新键
        if salesman_id not in data[semester]:
            data[semester][salesman_id] = Decimal(0)

        # 将订单数量累加到对应的键值上
        data[semester][salesman_id] += Decimal(order_num)

    # 将数据转换为JSON格式，使用自定义的DecimalEncoder进行编码
    json_data = json.dumps(data, cls=DecimalEncoder)

    # 渲染模板并传递数据给HTML
    return render_template('index.html', total_price=total_price, data=json_data, percentage_change=percentage_change)


def total():
    # 连接到数据库
    cnx = mysql.connector.connect(user='root', password='1234',
                                  host='localhost', database='massage')

    # 创建游标对象
    cursor = cnx.cursor()

    # 执行查询
    query = "SELECT SUM(totalPrice) FROM `order` WHERE semester='Q4'"
    cursor.execute(query)

    # 获取查询结果
    result = cursor.fetchone()
    total_price = result[0] if result else 0

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()

    # 渲染模板并传递total_price变量给HTML
    return render_template('index.html', total_price=total_price)

@app.route('/customer')
def customer():
    return render_template('customer.html')

@app.route('/purchase')
def purchase():
    return render_template('purchase.html')

@app.route('/marketing')
def marketing():
    return render_template('marketing.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/kpi')
def kpi():
    return render_template('kpi.html')

@app.route('/chart')         #折線圖
def chart():
    # 连接到 MySQL 数据库
    cnx = mysql.connector.connect(user='root', password='1234',
                                  host='localhost', database='massage')
    cursor = cnx.cursor()

    # 准备查询
    query = "SELECT semester, orderNum FROM `order`"

    # 执行查询
    cursor.execute(query)

    # 提取结果
    results = cursor.fetchall()

    # 关闭连接
    cursor.close()
    cnx.close()

    # 创建字典来存储每个学期的订单总数
    data = {}

    # 遍历查询结果，计算每个学期的订单总数
    for row in results:
        semester = row[0]
        order_num = row[1]

        # 如果字典中没有该学期的键，则创建新键
        if semester not in data:
            data[semester] = 0

        # 将订单数量累加到对应的键值上
        data[semester] += order_num

    # 将结果转换为 JSON 格式，同时对每个学期的订单总数加 1
    json_data = [{'semester': semester, 'orderNum': order_num + 1} for semester, order_num in data.items()]

    return json.dumps(json_data)



if __name__ == '__main__':
    app.run()
