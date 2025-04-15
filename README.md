# 🛒 Inventory Management System (Kiryana Store)

A simple command-line-based Inventory Management System built with Python and SQLite. Designed to help small retail shops (like kiryana stores) manage products, track stock movements, and view current inventory levels with ease.

---

## 🚀 Features

- **Add Products**: Insert new items with name, price, and initial stock.
- **Update Stock**: Add new stock, record sales, or manually remove inventory.
- **View Stock**: Get a real-time summary of all products and their stock levels.
- **Persistent Storage**: Data is stored using SQLite for easy local access.
- **Error Handling**: User input and database operations are handled with care to ensure a smooth experience.

---

## 🧾 Tables Used

- **products**: Stores product details.
- **current_stock**: Tracks real-time stock per product.
- **stock_movements**: Logs all stock-related transactions (in, sale, removal).

---

## 📦 How to Run

1. **Make sure Python is installed**  
   (Test with: `python --version`)

2. **Clone or download this repository**

3. **Run the script**  
   ```bash
   python IMS.py
