import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from config import Config

def get_product_details(product_id):
    # Read data from multiple sheets
    print("Get product details")
    products_df = pd.read_excel('Data.xlsx', sheet_name='products (2)')
    variants_df = pd.read_excel('Data.xlsx', sheet_name='products_variants (2)')
    memories_df = pd.read_excel('Data.xlsx', sheet_name='memories (2)')
    colors_df = pd.read_excel('Data.xlsx', sheet_name='colors (2)')
    attributes_df = pd.read_excel('Data.xlsx', sheet_name='attributes (2)')
    attribute_values_df = pd.read_excel('Data.xlsx', sheet_name='attribute_values (2)')
    usage_categories_df = pd.read_excel('Data.xlsx', sheet_name='usage_categories (2)')  # Add usage categories

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

def content_based_filtering(db, customer_id, top_n=5):

    # 📌 1. Lấy danh sách sản phẩm mà user đã xem
    query = "SELECT product_id FROM user_actions WHERE customer_id = :customer_id AND action_type = 'view'"
    viewed_products = pd.read_sql(query, db.engine, params={"customer_id": customer_id})

    if viewed_products.empty:
        return get_trending_products(top_n)  # 📌 Fallback nếu không có dữ liệu

    # 📌 2. Lấy mô tả sản phẩm từ Product Service API
    # Update product data collection
    product_data = []
    for product_id in viewed_products["product_id"]:
        product_details = get_product_details(product_id)
        if product_details:
            product_data.append({
                "id": product_details["id"],
                "name": product_details["name"],
                "category": product_details["category"],
                "description": product_details["description"],
                "memories": product_details.get("memories", ""),
                "colors": product_details.get("colors", ""),
                "screen": product_details.get("screen", ""),
                "battery": product_details.get("battery", ""),
                "processor": product_details.get("processor", ""),
                "camera": product_details.get("camera", ""),
                "os": product_details.get("os", "")
            })

    if not product_data:
        return get_trending_products(top_n)  # 📌 Fallback nếu API không trả về dữ liệu

    df = pd.DataFrame(product_data)

    # 📌 3. Tính độ tương đồng giữa sản phẩm bằng TF-IDF + Cosine Similarity
    # Update TF-IDF matrix creation
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(
        df['name'] + " " + 
        df['category'] + " " + 
        df['description'] + " " + 
        df['memories'] + " " + 
        df['colors'] + " " + 
        df['screen'] + " " + 
        df['battery'] + " " + 
        df['processor'] + " " + 
        df['camera'] + " " + 
        df['os']
    )
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
