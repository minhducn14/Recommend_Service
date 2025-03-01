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

def get_product_details(product_id):
    # Read data from multiple sheets
    products_df = pd.read_excel('Data.xlsx', sheet_name='products (2)')
    variants_df = pd.read_excel('Data.xlsx', sheet_name='products_variants (2)')
    memories_df = pd.read_excel('Data.xlsx', sheet_name='memories (2)')
    colors_df = pd.read_excel('Data.xlsx', sheet_name='colors (2)')
    attributes_df = pd.read_excel('Data.xlsx', sheet_name='attributes (2)')
    attribute_values_df = pd.read_excel('Data.xlsx', sheet_name='attribute_values (2)')
    usage_categories_df = pd.read_excel('Data.xlsx', sheet_name='usage_categories (2)')

    # Get base product info
    product = products_df[products_df['id'] == product_id].to_dict('records')
    if not product:
        return None
    
    product = product[0]
    
    # Get variants info
    variants = variants_df[variants_df['product_id'] == product_id]
    if not variants.empty:
        # Get category info
        category_id = variants['usage_category_id'].iloc[0]
        category_info = usage_categories_df[usage_categories_df['id'] == category_id]['name'].iloc[0]
        product['category'] = category_info

        # Create description from product name and category
        product['description'] = f"{product['name']} - {category_info}"

        # Rest of the variant processing
        variant_details_df = pd.read_excel('Data.xlsx', sheet_name='product_variant_details (2)')
        variant_details = variant_details_df[variant_details_df['product_variant_id'].isin(variants['id'])]
        memory_info = memories_df[memories_df['id'].isin(variant_details['memory_id'])]['id'].tolist()
        color_info = colors_df[colors_df['id'].isin(variant_details['color_id'])]['id'].tolist()
        product['memories'] = ', '.join(memory_info)
        product['colors'] = ', '.join(color_info)

    # Get attribute values
    product_attributes = attribute_values_df[attribute_values_df['product_variant_id'].isin(variants['id'])]
    for _, attr in product_attributes.iterrows():
        attr_name = attributes_df[attributes_df['id'] == attr['attribute_id']]['name'].iloc[0]
        product[attr_name.lower()] = attr['value']

    return product

def collaborative_filtering(db, customer_id, top_n=5):
    # 📌 1. Lấy dữ liệu từ Excel
    df = pd.read_excel('Data.xlsx', sheet_name='user_actions (2)')
    
    if df.empty:
        return get_trending_products(top_n)

    # 📌 2. Gán trọng số cho từng hành động
    df["weight"] = df["action_type"].map(ACTION_WEIGHTS)

    # 📌 3. Xây dựng ma trận User-Item
    user_product_matrix = df.pivot_table(
        index="customer_id", 
        columns="product_id", 
        values="weight", 
        aggfunc="sum", 
        fill_value=0
    )

    # 📌 4. Tính toán độ tương đồng giữa người dùng
    similarity_matrix = cosine_similarity(user_product_matrix)
    similarity_df = pd.DataFrame(
        similarity_matrix, 
        index=user_product_matrix.index, 
        columns=user_product_matrix.index
    )

    # 📌 5. Lấy danh sách người dùng có hành vi giống `customer_id`
    similar_users = similarity_df.get(customer_id)
    if similar_users is None:
        return get_trending_products(top_n)

    similar_users = similar_users.sort_values(ascending=False)[1:6]

    # 📌 6. Lấy sản phẩm từ user tương tự và chi tiết sản phẩm
    recommended_products = user_product_matrix.loc[similar_users.index].sum().sort_values(ascending=False)
    
    # Get detailed product information
    product_recommendations = []
    for product_id in recommended_products.index[:top_n]:
        product_details = get_product_details(product_id)
        if product_details:
            product_recommendations.append(product_id)

    return product_recommendations

def get_trending_products(top_n=5):
    """📌 Trả về danh sách sản phẩm thịnh hành nếu không có dữ liệu"""
    df = pd.read_excel('Data.xlsx', sheet_name='user_actions (2)')
    trending_products = df['product_id'].value_counts().head(top_n).index.tolist()
    return trending_products
