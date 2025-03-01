from fastapi import FastAPI
import uvicorn
import pandas as pd

app = FastAPI()

def get_mock_products():
    # Read data from Excel sheets
    products_df = pd.read_excel('Data.xlsx', sheet_name='products (2)')
    variants_df = pd.read_excel('Data.xlsx', sheet_name='products_variants (2)')
    memories_df = pd.read_excel('Data.xlsx', sheet_name='memories (2)')
    colors_df = pd.read_excel('Data.xlsx', sheet_name='colors (2)')
    attributes_df = pd.read_excel('Data.xlsx', sheet_name='attributes (2)')
    attribute_values_df = pd.read_excel('Data.xlsx', sheet_name='attribute_values (2)')
    usage_categories_df = pd.read_excel('Data.xlsx', sheet_name='usage_categories (2)')

    # Create mock products dictionary
    MOCK_PRODUCTS = {}
    
    for _, product in products_df.iterrows():
        product_id = product['id']
        product_data = {
            "id": product_id,
            "name": product['name']
        }
        
        # Get variants info
        variants = variants_df[variants_df['product_id'] == product_id]
        if not variants.empty:
            # Get category
            category_id = variants['usage_category_id'].iloc[0]
            category_info = usage_categories_df[usage_categories_df['id'] == category_id]['name'].iloc[0]
            product_data['category'] = category_info
            
            # Get variant details
            variant_details_df = pd.read_excel('Data.xlsx', sheet_name='product_variant_details (2)')
            variant_details = variant_details_df[variant_details_df['product_variant_id'].isin(variants['id'])]
            
            # Get memory and color info
            memory_info = memories_df[memories_df['id'].isin(variant_details['memory_id'])]['id'].tolist()
            color_info = colors_df[colors_df['id'].isin(variant_details['color_id'])]['id'].tolist()
            product_data['memories'] = ', '.join(str(m) for m in memory_info)
            product_data['colors'] = ', '.join(str(c) for c in color_info)

            # Get attribute values
            product_attributes = attribute_values_df[attribute_values_df['product_variant_id'].isin(variants['id'])]
            for _, attr in product_attributes.iterrows():
                attr_name = attributes_df[attributes_df['id'] == attr['attribute_id']]['name'].iloc[0]
                product_data[attr_name.lower()] = attr['value']

        MOCK_PRODUCTS[product_id] = product_data

    return MOCK_PRODUCTS

# Initialize mock products
MOCK_PRODUCTS = get_mock_products()

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    return MOCK_PRODUCTS.get(product_id)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)