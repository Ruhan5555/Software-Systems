import sqlite3
from datetime import datetime

conn = sqlite3.connect('store.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name STRING NOT NULL UNIQUE, -- Added UNIQUE constraint
        price REAL,
        date_added DATETIME
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        action STRING CHECK(action IN ('stock_in', 'sale', 'manual_removal')),
        quantity INTEGER, -- Store absolute quantity moved
        timestamp DATETIME,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS current_stock (
        product_id INTEGER PRIMARY KEY,
        quantity INTEGER NOT NULL DEFAULT 0,
        last_updated DATETIME,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')

conn.commit()

def add_product():
    """Adds a new product and its initial stock."""
    try:
        name = input("\nEnter product name (e.g., 'Sugar'): ").strip()
        if not name:
            print("Error: Product name cannot be empty.")
            return

        price_str = input("Enter product price (e.g., 50): ").strip()
        price = float(price_str)

        init_quantity_str = input("Enter initial stock quantity (e.g., 100): ").strip()
        init_quantity = int(init_quantity_str)

        if price < 0 or init_quantity < 0:
            print("Error: Price and initial quantity cannot be negative.")
            return

        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute('''INSERT INTO products (name, price, date_added) VALUES (?, ?, ?)''', (name, price, date_added))
            product_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO current_stock (product_id, quantity, last_updated) VALUES (?, ?, ?)''', (product_id, init_quantity, date_added))

            if init_quantity > 0:
                cursor.execute('''
                    INSERT INTO stock_movements (product_id, action, quantity, timestamp) VALUES (?, ?, ?, ?) ''', (product_id, 'stock_in', init_quantity, date_added))

            conn.commit()
            print(f"Product '{name}' added with ID: {product_id} and initial stock: {init_quantity}!")

        except sqlite3.IntegrityError:
            conn.rollback()
            print(f"Error: Product name '{name}' already exists.")
        except Exception as e:
            conn.rollback()
            print(f"An error occurred during database operation: {e}")

    except ValueError:
        print("Invalid input! Please enter valid numbers for price and quantity.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def update_stock():
    """Updates stock for a product (Add, Sell, Remove)."""
    try:
        cursor.execute('''
            SELECT p.id, p.name, p.price, cs.quantity
            FROM products p
            LEFT JOIN current_stock cs ON p.id = cs.product_id
            ORDER BY p.id
        ''')
        products = cursor.fetchall()

        if not products:
            print("\nNo products found. Add a product first!")
            return

        print("\nAvailable Products:")
        print("{:<5} {:<20} {:<10} {:<10}".format('ID', 'Product', 'Price', 'Quantity'))
        print("-" * 47)
        for item in products:
            quantity = item['quantity'] if item['quantity'] is not None else 0
            price = item['price'] if item['price'] is not None else 0.0
            print("{:<5} {:<20} Rs. {:<9.2f} {:<10}".format(item['id'], item['name'], price, quantity))
        print("-" * 47)

        product_id_str = input("\nEnter product ID to update stock: ").strip()
        product_id = int(product_id_str)

        cursor.execute("SELECT quantity FROM current_stock WHERE product_id = ?", (product_id,))
        stock_data = cursor.fetchone()
        if stock_data is None:
             cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
             product_data = cursor.fetchone()
             if product_data is None:
                 print(f"Error: Product with ID {product_id} does not exist.")
             else:
                 print(f"Error: Product ID {product_id} found but has no stock record. Please check data integrity.")
             return
        current_quantity = stock_data['quantity']

        action_choice = input('''
Choose action:
1. Add Stock (Stock In)
2. Sell Stock (Sale)
3. Remove Stock (Manual Removal)
Enter your choice (1-3): ''').strip()

        action_map = {'1': 'stock_in', '2': 'sale', '3': 'manual_removal'}
        action = action_map.get(action_choice)

        if not action:
            print("Invalid action choice!")
            return

        quantity_str = input(f"Enter quantity to {action.replace('_', ' ')}: ").strip()
        quantity_change = int(quantity_str)

        if quantity_change <= 0:
            print("Error: Quantity must be a positive number.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_quantity_change = quantity_change 
        movement_quantity = quantity_change 

        if action in ('sale', 'manual_removal'):
            if quantity_change > current_quantity:
                print(f"Error: Insufficient stock for Product ID {product_id}. Available: {current_quantity}, Tried to {action}: {quantity_change}")
                return
            final_quantity_change = -quantity_change

        try:
            cursor.execute('''
                INSERT INTO stock_movements (product_id, action, quantity, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (product_id, action, movement_quantity, timestamp))

            cursor.execute('''
                UPDATE current_stock
                SET quantity = quantity + ?, last_updated = ?
                WHERE product_id = ?
            ''', (final_quantity_change, timestamp, product_id))

            conn.commit()
            print(f"Stock updated successfully for Product ID {product_id}!")
            cursor.execute("SELECT quantity FROM current_stock WHERE product_id = ?", (product_id,))
            new_stock = cursor.fetchone()
            print(f"New stock level: {new_stock['quantity']}")


        except Exception as e:
            conn.rollback() # Rollback transaction on any error during DB operations
            print(f"An error occurred during database update: {e}")

    except ValueError:
        print("Invalid input! Please enter numeric values for ID and quantity.")
    except Exception as e:
        print(f"An unexpected error occurred in update_stock: {e}")


def view_stock():
    """Displays the current stock levels for all products."""
    try:
        cursor.execute('''
            SELECT p.id, p.name, p.price, cs.quantity
            FROM products p
            LEFT JOIN current_stock cs ON p.id = cs.product_id
            ORDER BY p.id
        ''')
        stock = cursor.fetchall()

        if not stock:
            print("\nNo stock data found. Add some products first.")
            return

        print("\nCurrent Stock Levels:")
        print("{:<5} {:<20} {:<10} {:<10}".format('ID', 'Product', 'Price', 'Quantity'))
        print("-" * 47)
        for item in stock:
            quantity = item['quantity'] if item['quantity'] is not None else 0
            price = item['price'] if item['price'] is not None else 0.0
            print("{:<5} {:<20} Rs. {:<9.2f} {:<10}".format(item['id'], item['name'], price, quantity))
        print("-" * 47)

    except Exception as e:
        print(f"An error occurred while viewing stock: {e}")


def main_menu():
    """Displays the main menu and handles user choices."""
    print("\nInitializing Kiryana Store System...")
    print("System Ready.")

    while True:
        print('''
\n===== Kiryana Store System =====
1. Add Product & Initial Stock
2. Update Stock (Add/Sell/Remove)
3. View Current Stock
4. Exit
===============================''')
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            add_product()
        elif choice == '2':
            update_stock()
        elif choice == '3':
            view_stock()
        elif choice == '4':
            print("\nExiting system. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"\nA critical error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")