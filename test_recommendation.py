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
        'customer_id': [
            '8d0a333c-d274-4f34-a250-0acc5f99f471',  
            '8d0a333c-d274-4f34-a250-0acc5f99f471',
            '8d0a333c-d274-4f34-a250-0acc5f99f471',
            'b6a9c856-5d6c-43b1-84b5-38c95d7e4ebe',  
            'b6a9c856-5d6c-43b1-84b5-38c95d7e4ebe',
            'b6a9c856-5d6c-43b1-84b5-38c95d7e4ebe',
            'd9ae2c91-7c44-4ca3-a9b9-292f6f7d8d42',  
            'd9ae2c91-7c44-4ca3-a9b9-292f6f7d8d42',
            'd9ae2c91-7c44-4ca3-a9b9-292f6f7d8d42'
        ],
        'product_id': [
            "bd5b6aa1-69c6-4207-8642-8b5ceaf065ad", 
            "c9de2a34-0b4a-4df5-9ac6-b5e3cde1ff95", 
            "a15b85f1-cfba-4510-86fe-ef9cdf2b10a2",  
            "11dda71a-ec77-4d72-b6d4-1b869f727a9e",
            "dd55204d-7dcb-4598-982e-262c69767f50", 
            "77381ee5-6c1a-41a6-becf-d2def8e197e3",
            "828a961c-c4aa-405d-bc9b-c9aa01cd473a",
            "9bffb182-abaa-43bf-bb86-4d99d2dfa5ed",
            "11dda71a-ec77-4d72-b6d4-1b869f727a9e"
        ],
        'action_type': ['view'] * 9,
        'action_timestamp': pd.date_range(start='2024-01-01', periods=9)
    })
    
    test_data.to_sql('user_actions', engine, if_exists='replace', index=False)
    return engine

def test_recommendations():
    db = MockDB()
    
    # Get unique customer IDs using SQLAlchemy text query
    from sqlalchemy import text
    with db.engine.connect() as connection:
        result = connection.execute(text("SELECT DISTINCT customer_id FROM user_actions"))
        customer_ids = [row[0] for row in result]
    
    for test_customer_id in customer_ids:
        print("*" * 50)
        print(f"\nTesting recommendations for customer {test_customer_id}")
        print("=" * 50)
        
        try:
            recommendations = content_based_filtering(db, test_customer_id, top_n=3)
            print(f"Recommended products: {recommendations}")
            print("-" * 50)

            print("\nRecommended Product Details:")
            print("=" * 50)
            for product_id in recommendations:
                product = get_product_details(product_id)
                if product:
                    print(f"Name: {product['name']}")
                else:
                    print(f"Product {product_id} not found")
        except Exception as e:
            print(f"Error during recommendation: {str(e)}")

if __name__ == "__main__":
    test_recommendations()