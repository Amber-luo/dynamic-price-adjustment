import mysql.connector
import random
from datetime import datetime, timedelta
import numpy as np

print("=== 开始执行数据生成脚本 ===")

try:
    # 连接 MySQL
    print("正在连接 MySQL...")
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="960917",  # 改成你的密码
        database="ecommerce"
    )
    cursor = conn.cursor()
    print("✅ MySQL 连接成功")

    # 生成模拟数据
    products = ['A001', 'A002', 'A003', 'A004', 'A005']
    start_date = datetime(2025, 1, 1)
    np.random.seed(42)

    for day in range(60):
        date = start_date + timedelta(days=day)
        for product in products:
            own_price = round(random.uniform(80, 120), 2)
            competitor_price = round(own_price + random.uniform(-10, 10), 2)
            cost = round(own_price * random.uniform(0.6, 0.8), 2)
            stock = random.randint(50, 500)

            cursor.execute("""
                INSERT INTO product_price (date, product_id, own_price, competitor_price, cost, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (date, product, own_price, competitor_price, cost, stock))

    conn.commit()
    print("✅ 数据写入完成")

except Exception as e:
    print("❌ 发生错误：", e)

finally:
    if 'conn' in locals():
        conn.close()
        print("🔒 MySQL 连接已关闭")

print("=== 数据生成脚本结束 ===")
