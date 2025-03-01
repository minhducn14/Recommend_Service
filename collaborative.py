import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 📌 Trọng số cho từng loại hành vi
ACTION_WEIGHTS = {
    "purchase": 10,
    "add_to_cart": 7,
    "click": 5,
    "view": 3,
    "search": 1
}

def collaborative_filtering(db, customer_id, top_n=5):

    # 📌 1. Lấy dữ liệu từ database
    query = "SELECT customer_id, product_id, action_type FROM user_actions"
    df = pd.read_sql(query, db.engine)

    if df.empty:
        return get_trending_products(top_n)  # 📌 Cold Start: Lấy sản phẩm thịnh hành

    # 📌 2. Gán trọng số cho từng hành động
    df["weight"] = df["action_type"].map(ACTION_WEIGHTS)

    # 📌 3. Xây dựng ma trận User-Item
    user_product_matrix = df.pivot_table(index="customer_id", columns="product_id", values="weight", aggfunc="sum", fill_value=0)

    # 📌 4. Tính toán độ tương đồng giữa người dùng
    similarity_matrix = cosine_similarity(user_product_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_product_matrix.index, columns=user_product_matrix.index)

    # 📌 5. Lấy danh sách người dùng có hành vi giống `customer_id`
    similar_users = similarity_df.get(customer_id)
    if similar_users is None:
        return get_trending_products(top_n)  # 📌 Cold Start nếu user mới

    similar_users = similar_users.sort_values(ascending=False)[1:6]  # Lấy top 5 user tương tự

    # 📌 6. Lấy sản phẩm từ user tương tự
    recommended_products = user_product_matrix.loc[similar_users.index].sum().sort_values(ascending=False).index.tolist()

    return recommended_products[:top_n]
