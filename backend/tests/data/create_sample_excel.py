import pandas as pd
import random
from datetime import datetime, timedelta

def generate_sample_sales_data():
    """
    Generate 100+ rows of realistic sales data
    
    Columns:
    - Date: Transaction date (2024 full year)
    - Product: 8 different tech products
    - Quantity: 1-10 units per order
    - Price: $10-$500 per unit
    - Customer: 50 different customers
    - Region: North, South, East, West
    """

    # Product catalog with realistic prices
    products = [
        'Laptop',
        'Mouse',
        'Keyboard',
        'Monitor',
        'Headphones',
        'Webcam',
        'USB Cable',
        'Desk Lamp'
    ]

    regions = ['North', 'South', 'East', 'West']
    customers = [f'Customer_{i:03d}' for i in range(1, 51)]  # Customer_001 to Customer_050

    data = []
    start_date = datetime(2024, 1, 1)

    # Generate 150 orders for better analysis
    for i in range(150):
        date = start_date + timedelta(days=random.randint(0, 365))
        product = random.choice(products)
        quantity = random.randint(1, 10)

        # Price varies by product type
        if product == 'Laptop':
            price = round(random.uniform(800, 1500), 2)
        elif product == 'Monitor':
            price = round(random.uniform(200, 600), 2)
        elif product == 'Headphones':
            price = round(random.uniform(50, 300), 2)
        elif product in ['Mouse', 'Keyboard']:
            price = round(random.uniform(20, 100), 2)
        else:
            price = round(random.uniform(10, 80), 2)

        customer = random.choice(customers)
        region = random.choice(regions)

        # Calculate total revenue for this order
        revenue = round(quantity * price, 2)

        data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Product': product,
            'Quantity': quantity,
            'Price': price,
            'Revenue': revenue,
            'Customer': customer,
            'Region': region
        })

    # Create DataFrame and sort by date
    df = pd.DataFrame(data)
    df = df.sort_values('Date').reset_index(drop=True)

    # Save to both CSV and Excel formats
    df.to_csv('sample_sales_data.csv', index=False)
    df.to_excel('sample_sales_data.xlsx', index=False, engine='openpyxl')

    # Print summary statistics
    print("✅ Sample sales data created successfully!")
    print(f"\nDataset Statistics:")
    print(f"- Total orders: {len(df)}")
    print(f"- Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"- Total revenue: ${df['Revenue'].sum():,.2f}")
    print(f"- Average order value: ${df['Revenue'].mean():.2f}")
    print(f"- Unique customers: {df['Customer'].nunique()}")
    print(f"- Unique products: {df['Product'].nunique()}")
    print(f"\nFiles created:")
    print("- sample_sales_data.csv")
    print("- sample_sales_data.xlsx")

if __name__ == "__main__":
    generate_sample_sales_data()

