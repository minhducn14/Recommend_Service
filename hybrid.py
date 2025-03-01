def hybrid_recommendation(db, customer_id, top_n=5):

    # 📌 1. Lấy kết quả từ từng mô hình
    collaborative_results = collaborative_filtering(db, customer_id, top_n * 2)  # Lấy gấp đôi để loại trùng sau
    content_based_results = content_based_filtering(db, customer_id, top_n * 2)

    # 📌 2. Áp dụng chiến lược loại bỏ trùng lặp & trọng số
    combined_results = []
    seen = set()

    for product in collaborative_results + content_based_results:
        if product not in seen:
            combined_results.append(product)
            seen.add(product)

        if len(combined_results) >= top_n:
            break  # Chỉ lấy số lượng cần thiết

    return combined_results
