from content_based import content_based_filtering, get_product_details
from sqlalchemy import create_engine
import pandas as pd

class MockDB:
    def __init__(self):
        self.engine = setup_test_db()

def setup_test_db():
    """Create a test database connection"""
    DATABASE_URL = "sqlite:///test.db"  
    engine = create_engine(DATABASE_URL)
    
    test_data = pd.DataFrame({
        'customer_id': [1, 1, 1, 2],
        'product_id': [
            "11dda71a-ec77-4d72-b6d4-1b869f727a9e",
            "77381ee5-6c1a-41a6-becf-d2def8e197e3",
            "828a961c-c4aa-405d-bc9b-c9aa01cd473a",
            "9bffb182-abaa-43bf-bb86-4d99d2dfa5ed"
        ],
        'action_type': ['view', 'view', 'view', 'view'],
        'action_timestamp': pd.date_range(start='2024-01-01', periods=4)
    })
    
    test_data.to_sql('user_actions', engine, if_exists='replace', index=False)
    return engine

def test_recommendations():
    db = MockDB()
    test_customer_id = 1
    
    print(f"\nTesting recommendations for customer {test_customer_id}")
    print("=" * 50)
    
    try:
        recommendations = content_based_filtering(db, test_customer_id, top_n=3)
        print(f"Recommended products: {recommendations}")
        
        print("\nRecommended Product Details:")
        print("=" * 50)
        for product_id in recommendations:
            product = get_product_details(product_id)
            if product:
                print(f"Product ID: {product['id']}")
                print(f"Name: {product['name']}")
                print(f"Category: {product['category']}")
                print(f"Description: {product['description']}")
                print("-" * 30)
            else:
                print(f"Product {product_id} not found")
    except Exception as e:
        print(f"Error during recommendation: {str(e)}")

if __name__ == "__main__":
    test_recommendations()