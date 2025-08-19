import pymysql
import pandas as pd

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "960917",
    "database": "ecommerce",
    "charset": "utf8mb4"
}

def get_data():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        query = "SELECT * FROM product_price;"
        df = pd.read_sql(query, conn)
        conn.close()
        print(f"[INFO] 数据读取成功，共 {len(df)} 条记录")
        return df
    except Exception as e:
        print(f"[ERROR] 数据读取失败: {e}")
        return None

def analyse_data(df):
    print("\n[INFO] 开始分析数据...")
    if df is None or df.empty:
        print("[WARNING] 没有数据可分析")
        return

    print("\n===== 基础统计 =====")
    print(df.describe())

    print("\n===== 按产品统计平均价格 =====")
    avg_price = df.groupby("product_id")["own_price"].mean().reset_index()
    print(avg_price)

    print("\n===== 价格波动（标准差） =====")
    price_std = df.groupby("product_id")["own_price"].std().reset_index()
    print(price_std)

def adjust_price(df):
    df['price_diff'] = df['own_price'] - df['competitor_price']
    df['profit_margin'] = (df['own_price'] - df['cost']) / df['own_price']
    df['suggested_price'] = df['own_price']  # 默认不变

    df.loc[df['price_diff'] > 5, 'suggested_price'] = df['own_price'] - 3
    df.loc[df['price_diff'] < -5, 'suggested_price'] = df['own_price'] + 3

    print("\n[INFO] 调价建议预览：")
    print(df[['product_id', 'own_price', 'competitor_price', 'suggested_price']].head())

    return df

def write_data(df):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 如果没有列则添加
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME='product_price' AND COLUMN_NAME='suggested_price'
    """, (DB_CONFIG['database'],))
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            ALTER TABLE product_price
            ADD COLUMN suggested_price DECIMAL(10,2) NULL
        """)

    # 更新
    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE product_price
            SET suggested_price = %s
            WHERE id = %s
        """, (row['suggested_price'], row['id']))

    conn.commit()
    conn.close()
    print("[INFO] 调价建议已写回 MySQL")

if __name__ == "__main__":
    df = get_data()
    analyse_data(df)
    adjusted_df = adjust_price(df)
    write_data(adjusted_df)
