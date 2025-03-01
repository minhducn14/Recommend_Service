from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Mock product data based on your Excel data
MOCK_PRODUCTS = {
    "11dda71a-ec77-4d72-b6d4-1b869f727a9e": {
        "id": "11dda71a-ec77-4d72-b6d4-1b869f727a9e",
        "name": "Samsung Galaxy A55 5G2",
        "category": "Smartphone",
        "description": "Latest Samsung A-series smartphone with 5G capability",
        "trademark_id": "7b8c08a0-a860-46ff-bdf1-952a32d973ea"
    },
    "77381ee5-6c1a-41a6-becf-d2def8e197e3": {
        "id": "77381ee5-6c1a-41a6-becf-d2def8e197e3",
        "name": "OPPO Reno12",
        "category": "Smartphone",
        "description": "OPPO Reno series with advanced camera features",
        "trademark_id": "9be493a9-9f25-4861-a8f9-7a1c7e84eb3e"
    },
    "828a961c-c4aa-405d-bc9b-c9aa01cd473a": {
        "id": "828a961c-c4aa-405d-bc9b-c9aa01cd473a",
        "name": "Samsung Galaxy S23 8GB",
        "category": "Smartphone",
        "description": "Samsung flagship with 8GB RAM configuration",
        "trademark_id": "7b8c08a0-a860-46ff-bdf1-952a32d973ea"
    },
    "9bffb182-abaa-43bf-bb86-4d99d2dfa5ed": {
        "id": "9bffb182-abaa-43bf-bb86-4d99d2dfa5ed",
        "name": "Sony Xperia",
        "category": "Smartphone",
        "description": "Sony's premium smartphone with advanced display",
        "trademark_id": "c1021e5c-c2d9-424a-9b15-eb350d3f21a2"
    },
    "a15b85f1-cfba-4510-86fe-ef9cdf2b10a2": {
        "id": "a15b85f1-cfba-4510-86fe-ef9cdf2b10a2",
        "name": "Samsung Galaxy Z Flip5",
        "category": "Smartphone",
        "description": "Foldable smartphone with innovative design",
        "trademark_id": "7b8c08a0-a860-46ff-bdf1-952a32d973ea"
    },
    "bd5b6aa1-69c6-4207-8642-8b5ceaf065ad": {
        "id": "bd5b6aa1-69c6-4207-8642-8b5ceaf065ad",
        "name": "Samsung Galaxy S23 Ultra",
        "category": "Smartphone",
        "description": "Premium flagship with S-Pen support",
        "trademark_id": "7b8c08a0-a860-46ff-bdf1-952a32d973ea"
    },
    "c9de2a34-0b4a-4df5-9ac6-b5e3cde1ff95": {
        "id": "c9de2a34-0b4a-4df5-9ac6-b5e3cde1ff95",
        "name": "Samsung Galaxy S23U 8GB",
        "category": "Smartphone",
        "description": "Ultra model with 8GB RAM configuration",
        "trademark_id": "7b8c08a0-a860-46ff-bdf1-952a32d973ea"
    },
    "dd55204d-7dcb-4598-982e-262c69767f50": {
        "id": "dd55204d-7dcb-4598-982e-262c69767f50",
        "name": "Samsung Galaxy A35 5G",
        "category": "Smartphone",
        "description": "Mid-range 5G smartphone with great value",
        "trademark_id": "7b8c08a0-a860-46ff-bdf1-952a32d973ea"
    }
}

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    return MOCK_PRODUCTS.get(product_id)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)