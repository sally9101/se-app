import mysql.connector
from flask import Flask, render_template, request
import json
from decimal import Decimal  # Add this line
import pymysql

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

app = Flask(__name__)

def get_db_connection():
    # 连接到MySQL数据库
    cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='massage'
)
    return cnx

@app.route('/')
def index():
    cnx = get_db_connection()
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

    # 连接到MySQL数据库
    cnx = mysql.connector.connect(user='root', password='1234',
                                  host='localhost', database='massage')

    # 创建游标对象
    cursor = cnx.cursor()

    # 执行查询
    query = "SELECT semester, productId, SUM(orderNum) FROM `order` GROUP BY semester, productId"
    cursor.execute(query)

    # 获取查询结果
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
    # Close the cursor and connection
    cursor.close()
    cnx.close()

    cnx = get_db_connection()
    cursor = cnx.cursor()

    query = """
    SELECT product.productName, SUM(`order`.totalPrice) AS totalPrice
    FROM product
    JOIN `order` ON product.productId = `order`.productId
    GROUP BY product.productId
    ORDER BY product.productId
    """
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    chart_data = {
        'labels': [row[0] for row in results],
        'datasets': [{
            'label': 'Total Price',
            'data': [row[1] for row in results],
            'backgroundColor': 'rgba(0, 123, 255, 0.5)',
            'borderColor': 'rgba(0, 123, 255, 1)',
            'borderWidth': 1,
        }]
    }

    chart_json = json.dumps(chart_data, cls=DecimalEncoder)

    cnx = get_db_connection()
    cursor = cnx.cursor()
###########################################################################
    sql = "SELECT salesName, orderNum, sellMoney FROM salesman"
    cursor.execute(sql)
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    # 整理資料為適合傳送到前端的格式
    chart_data = []
    for row in results:
       chart_data.append([row[0], row[1], row[2]])

    chart_data_json = json.dumps(chart_data, cls=DecimalEncoder)

   # 获取数据库连接
    cnx = get_db_connection()

    # 创建游标对象
    cursor = cnx.cursor()

    # 执行查询语句，计算sellTarget列的总和
    cursor.execute("SELECT SUM(sellTarget) FROM salesman")

    # 获取查询结果
    result = cursor.fetchone()
    total_sell_target = result[0] if result[0] else 0

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()

    cnx = get_db_connection()
    cursor = cnx.cursor()
    # 查询sellMoney和sellTarget的总和
    cursor.execute("SELECT SUM(sellMoney), SUM(sellTarget) FROM salesman")

    result = cursor.fetchone()
    total_sell_money = result[0]
    total_sell_target = result[1]

    # 计算销售目标达成率
    achievement_rate = (total_sell_money / total_sell_target) * 100
    achievement_rate = round(achievement_rate, 1)

    cursor.close()
    cnx.close()

    # 获取数据库连接
    cnx = get_db_connection()

    # 创建游标对象
    cursor = cnx.cursor()

    query = "SELECT place, SUM(rentMoney) AS rentMoneySum, SUM(totalMoney) AS totalMoneySum FROM public GROUP BY place"
    cursor.execute(query)

    # 提取查询结果
    data1 = []
    placeLabels = []
    rentMoneySumData = []
    totalMoneySumData = []
    for row in cursor.fetchall():
        place = row[0]
        rentMoneySum = float(row[1])
        totalMoneySum = float(row[2])
        
        data1.append({
            'place': place,
            'rentMoneySum': rentMoneySum,
            'totalMoneySum': totalMoneySum
        })
        placeLabels.append(place)
        rentMoneySumData.append(rentMoneySum)
        totalMoneySumData.append(totalMoneySum)

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()

    # 连接到MySQL数据库
    cnx = get_db_connection()
    cursor = cnx.cursor()
    query = '''
        SELECT orderNum, semester, productId
        FROM `order`
        ORDER BY semester, productId
    '''
    cursor.execute(query)
    data = cursor.fetchall()

    # 處理資料
    chart_data = {}
    semesters = set()
    products = set()
    for row in data:
        order_num = row[0]
        semester = row[1]
        product_id = row[2]

        if semester not in chart_data:
            chart_data[semester] = {}

        chart_data[semester][product_id] = order_num
        semesters.add(semester)
        products.add(product_id)

    # 建立堆疊長條圖的資料格式
    chart_datasets = []
    for product_id in sorted(products):
        data = []
        for semester in sorted(semesters):
            if semester in chart_data and product_id in chart_data[semester]:
                data.append(chart_data[semester][product_id])
            else:
                data.append(0)

        chart_datasets.append({
            'label': f'Product {product_id}',
            'data': data
        })

    chart_data_json_str = json.dumps({
        'labels': sorted(semesters),
        'datasets': chart_datasets
    })

    # 關閉資料庫連接
    cursor.close()
    cnx.close()
###########################################################
     # 建立cursor物件
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # 執行查詢
    query = "SELECT ticketName, UseTime FROM ticket"
    cursor.execute(query)

    # 擷取查詢結果
    results = cursor.fetchall()

    # 關閉cursor和連線
    cursor.close()
    cnx.close()

    # 將查詢結果轉換為字典列表
    data = []
    for row in results:
        data.append({'ticketName': row[0], 'UseTime': row[1]})

    # 將資料傳遞給HTML模板
    data_json = json.dumps(data)


    return render_template('index.html', total_price=total_price, percentage_change=percentage_change, 
                           json_data=json_data, data=data, chart_json=chart_json, chart_data=chart_data_json, 
                           total_sell_target=total_sell_target,achievement_rate=achievement_rate,
                           data1=data1, placeLabels=placeLabels,data_json=data_json,chart_data_json_str=chart_data_json_str,
                           rentMoneySumData=rentMoneySumData, totalMoneySumData=totalMoneySumData, chart_data1=chart_data)

    

cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234',
    database='massage'
)

@app.route('/search', methods=['POST'])
def search():
    # 获取用户输入
    search_term = request.form['search_term']

    # 创建游标对象
    cursor = cnx.cursor()

    # 在数据库中搜索
    query = "SELECT * FROM customer WHERE customerId LIKE '%{}%'".format(search_term)
    cursor.execute(query)

    # 获取搜索结果
    results = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 渲染搜索结果页面
    return render_template('results.html', results=results)


@app.route('/customer')
def customer():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute('SELECT * FROM customer')
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template('customer.html', customers=results)

@app.route('/search_order', methods=['POST'])
def searchorder():
    # 获取用户输入
    search_term = request.form['search_term']

    # 创建游标对象
    cursor = cnx.cursor()

    # 在数据库中搜索
    query = "SELECT * FROM `order` WHERE orderId LIKE '%{}%'".format(search_term)
    cursor.execute(query)

    # 获取搜索结果
    results2 = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 渲染搜索结果页面
    return render_template('orderresults.html', results2=results2)

@app.route('/purchase')
def purchase():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute('SELECT * FROM `order`')
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template('purchase.html', orders=results)

@app.route('/search_public', methods=['POST'])
def searchpublic():
    # 获取用户输入
    search_term = request.form['search_term']

    # 创建游标对象
    cursor = cnx.cursor()

    # 在数据库中搜索
    query = "SELECT * FROM public WHERE publicId LIKE '%{}%'".format(search_term)
    cursor.execute(query)

    # 获取搜索结果
    results2 = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 渲染搜索结果页面
    return render_template('publicresults.html', results2=results2)

@app.route('/marketing')
def marketing():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute('SELECT * FROM public')
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    return render_template('marketing.html', publics=results)

@app.route('/search_product', methods=['POST'])
def searchproduct():
    # 获取用户输入
    search_term = request.form['search_term']

    # 创建游标对象
    cursor = cnx.cursor()

    # 在数据库中搜索
    query = "SELECT * FROM product WHERE productId LIKE '%{}%'".format(search_term)
    cursor.execute(query)

    # 获取搜索结果
    results2 = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 渲染搜索结果页面
    return render_template('productresults.html', results2=results2)

@app.route('/sales')
def sales():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute('SELECT * FROM product')
    results = cursor.fetchall()

    query_total = "SELECT SUM(totalPrice) FROM `order` WHERE semester='Q4'"
    cursor.execute(query_total)
    result_total = cursor.fetchone()
    total_price = result_total[0] if result_total else 0

    cursor.close()
    cnx.close()

    return render_template('sales.html', sales=results, total_price=total_price)

@app.route('/search_kpi', methods=['POST'])
def searchkpi():
    # 获取用户输入
    search_term = request.form['search_term']

    # 创建游标对象
    cursor = cnx.cursor()

    # 在数据库中搜索
    query = "SELECT * FROM salesman WHERE salesmanId LIKE '%{}%'".format(search_term)
    cursor.execute(query)

    # 获取搜索结果
    results2 = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 渲染搜索结果页面
    return render_template('salesresults.html', results2=results2)

@app.route('/kpi')
def kpi():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    cursor.execute('SELECT * FROM salesman')
    results = cursor.fetchall()

    cursor.close()
    cnx.close()

    # 获取数据库连接
    cnx = get_db_connection()

    # 创建游标对象
    cursor = cnx.cursor()

    # 执行查询语句，计算sellTarget列的总和
    cursor.execute("SELECT SUM(sellTarget) FROM salesman")

    # 获取查询结果
    result = cursor.fetchone()
    total_sell_target = result[0] if result[0] else 0

    # 关闭游标和数据库连接
    cursor.close()
    cnx.close()

    return render_template('kpi.html', salesmans=results, total_sell_target=total_sell_target)

if __name__ == '__main__':
    app.run(debug=True)
