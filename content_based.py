import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from config import Config

def get_product_details(product_id):
    response = requests.get(f"{Config.PRODUCT_SERVICE_API}{product_id}")
    if response.status_code == 200:
        return response.json()
    return None

def content_based_filtering(db, customer_id, top_n=5):

    # 📌 1. Lấy danh sách sản phẩm mà user đã xem
    query = "SELECT product_id FROM user_actions WHERE customer_id = :customer_id AND action_type = 'view'"
    viewed_products = pd.read_sql(query, db.engine, params={"customer_id": customer_id})

    if viewed_products.empty:
        return get_trending_products(top_n)  # 📌 Fallback nếu không có dữ liệu

    # 📌 2. Lấy mô tả sản phẩm từ Product Service API
    product_data = []
    for product_id in viewed_products["product_id"]:
        product_details = get_product_details(product_id)
        if product_details:
            product_data.append({
                "id": product_details["id"],
                "name": product_details["name"],
                "category": product_details["category"],
                "description": product_details["description"]
            })

    if not product_data:
        return get_trending_products(top_n)  # 📌 Fallback nếu API không trả về dữ liệu

    df = pd.DataFrame(product_data)

    # 📌 3. Tính độ tương đồng giữa sản phẩm bằng TF-IDF + Cosine Similarity
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['name'] + " " + df['category'] + " " + df['description'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 📌 4. Gợi ý sản phẩm có mô tả giống với sản phẩm mà user đã xem
    indices = pd.Series(df.index, index=df['id'])
    recommended_products = cosine_sim[indices[df["id"].iloc[0]]].argsort()[-(top_n+1):-1][::-1]

    return df['id'].iloc[recommended_products].tolist()

def get_trending_products(top_n=5):
    """📌 Trả về danh sách sản phẩm thịnh hành nếu không có dữ liệu"""
    trending_query = "SELECT DISTINCT product_id FROM user_actions ORDER BY action_timestamp DESC LIMIT :top_n"
    trending_products = pd.read_sql(trending_query, db.engine, params={"top_n": top_n})
    return trending_products["product_id"].tolist() if not trending_products.empty else []
