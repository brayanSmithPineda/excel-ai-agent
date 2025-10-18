import pandas as pd
import random
from datetime import datetime, timedelta

def generate_quarterly_data(quarter, year=2024):
    """
    Generate sales data for a specific quarter
    
    Q1: Jan-Mar
    Q2: Apr-Jun
    Q3: Jul-Sep
    """

    # Define date ranges for each quarter
    quarter_dates = {
        1: (datetime(year, 1, 1), datetime(year, 3, 31)),
        2: (datetime(year, 4, 1), datetime(year, 6, 30)),
        3: (datetime(year, 7, 1), datetime(year, 9, 30))
    }

    start_date, end_date = quarter_dates[quarter]
    days_in_quarter = (end_date - start_date).days

    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam', 'USB Cable', 'Desk Lamp']
    regions = ['North', 'South', 'East', 'West']
    customers = [f'Customer_{i:03d}' for i in range(1, 51)]

    data = []

    # Generate 50 orders per quarter
    for i in range(50):
        date = start_date + timedelta(days=random.randint(0, days_in_quarter))
        product = random.choice(products)
        quantity = random.randint(1, 10)

        # Price varies by product
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

    df = pd.DataFrame(data)
    df = df.sort_values('Date').reset_index(drop=True)

    return df

def create_all_quarterly_files():
    """Create Q1, Q2, Q3 Excel files"""

    for quarter in [1, 2, 3]:
        df = generate_quarterly_data(quarter)
        filename = f'sales_q{quarter}_2024.xlsx'
        df.to_excel(filename, index=False, engine='openpyxl')

        print(f"✅ Created {filename}")
        print(f"   - Orders: {len(df)}")
        print(f"   - Total Revenue: ${df['Revenue'].sum():,.2f}")
        print(f"   - Date Range: {df['Date'].min()} to {df['Date'].max()}")
        print()

    print("🎉 All quarterly files created successfully!")
    print("\nFiles created:")
    print("- sales_q1_2024.xlsx (Jan-Mar)")
    print("- sales_q2_2024.xlsx (Apr-Jun)")
    print("- sales_q3_2024.xlsx (Jul-Sep)")

if __name__ == "__main__":
    create_all_quarterly_files()