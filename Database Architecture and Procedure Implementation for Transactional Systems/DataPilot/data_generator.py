import mysql.connector
import random
from datetime import datetime, timedelta
from faker import Faker
import os

# Initialize Faker
fake = Faker()

class DataGenerator:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', 'customersdb'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            return True
        except mysql.connector.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, data=None, many=False):
        """Execute a query"""
        try:
            cursor = self.connection.cursor()
            if many:
                cursor.executemany(query, data)
            else:
                cursor.execute(query, data)
            self.connection.commit()
            return cursor.lastrowid
        except mysql.connector.Error as e:
            print(f"Query execution error: {e}")
            return None
        finally:
            cursor.close()
    
    def clear_tables(self):
        """Clear existing data from all tables"""
        print("Clearing existing data...")
        
        # Disable foreign key checks
        self.execute_query("SET FOREIGN_KEY_CHECKS = 0")
        
        tables = ['log', 'shipping', 'orderitems', 'ordering', 'orders', 'inventory', 'price', 'products', 'employees', 'customers', 'category']
        
        for table in tables:
            self.execute_query(f"TRUNCATE TABLE {table}")
        
        # Re-enable foreign key checks
        self.execute_query("SET FOREIGN_KEY_CHECKS = 1")
        print("Data cleared successfully!")
    
    def generate_categories(self, count=20):
        """Generate category data"""
        print(f"Generating {count} categories...")
        
        categories = [
            "Electronics", "Clothing", "Home & Garden", "Sports & Outdoors", "Books",
            "Health & Beauty", "Toys & Games", "Automotive", "Food & Beverages", "Music",
            "Movies & TV", "Software", "Office Supplies", "Pet Supplies", "Jewelry",
            "Tools & Hardware", "Arts & Crafts", "Baby Products", "Travel", "Photography"
        ]
        
        category_data = []
        for i, cat_name in enumerate(categories[:count]):
            category_data.append((
                cat_name,
                fake.text(max_nb_chars=100),
                fake.date_time_between(start_date='-2y', end_date='now')
            ))
        
        query = "INSERT INTO category (category_name, description, updated_on) VALUES (%s, %s, %s)"
        self.execute_query(query, category_data, many=True)
        print(f"Generated {len(category_data)} categories")
    
    def generate_customers(self, count=1500):
        """Generate customer data"""
        print(f"Generating {count} customers...")
        
        customer_data = []
        used_emails = set()
        
        for _ in range(count):
            # Ensure unique email
            email = fake.email()
            while email in used_emails:
                email = fake.email()
            used_emails.add(email)
            
            customer_data.append((
                fake.first_name(),
                fake.last_name(),
                random.choice(['male', 'female', 'other', 'prefer not to say']),
                random.randint(18, 80),
                email,
                fake.phone_number()[:20],  # Limit to 20 chars
                fake.street_address(),
                fake.city(),
                fake.state(),
                fake.postcode(),
                fake.country(),
                fake.date_time_between(start_date='-3y', end_date='now')
            ))
        
        query = """INSERT INTO customers 
                   (first_name, last_name, gender, age, email, ph_num, address1, city, state, postal_code, country, registration_date) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, customer_data, many=True)
        print(f"Generated {len(customer_data)} customers")

    def generate_employees(self, count=100):
        """Generate employee data"""
        print(f"Generating {count} employees...")
        
        roles = ['Manager', 'Sales Rep', 'Developer', 'Analyst', 'Support', 'Admin', 'Marketing', 'HR']
        employee_data = []
        used_emails = set()
        
        for i in range(count):
            # Ensure unique email
            email = fake.email()
            while email in used_emails:
                email = fake.email()
            used_emails.add(email)
            
            # Some employees have managers (not the first ones)
            manager_id = random.randint(1, max(1, i//3)) if i > 5 else None
            
            employee_data.append((
                fake.first_name(),
                fake.last_name(),
                random.randint(22, 60),
                fake.phone_number()[:16],
                email,
                fake.date_between(start_date='-5y', end_date='-30d'),
                random.choice(roles),
                fake.date_between(start_date='-1y', end_date='now') if random.random() < 0.1 else None,  # 10% terminated
                manager_id,
                1 if random.random() > 0.1 else 0  # 90% still working
            ))
        
        query = """INSERT INTO employees 
                   (first_name, last_name, age, phone_number, email, hire_date, role, termination_date, manager_id, is_working) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, employee_data, many=True)
        print(f"Generated {len(employee_data)} employees")

    
    def generate_products(self, count=500):
        """Generate product data"""
        print(f"Generating {count} products...")
        
        product_types = [
            "Smartphone", "Laptop", "T-Shirt", "Jeans", "Sofa", "Table", "Basketball", "Book",
            "Shampoo", "Toy Car", "Wrench", "Paint", "Coffee", "Headphones", "Watch", "Backpack"
        ]
        
        product_data = []
        used_names = set()
        used_descriptions = set()
        
        for _ in range(count):
            # Ensure unique names and descriptions
            name = f"{fake.company()} {random.choice(product_types)} {fake.word()}"
            while name in used_names:
                name = f"{fake.company()} {random.choice(product_types)} {fake.word()}"
            used_names.add(name)
            
            description = fake.text(max_nb_chars=100)
            while description in used_descriptions:
                description = fake.text(max_nb_chars=100)
            used_descriptions.add(description)
            
            product_data.append((
                name[:50],  # Limit to 50 chars
                description[:100],  # Limit to 100 chars
                random.randint(1, 20)  # category_id
            ))
        
        query = "INSERT INTO products (product_name, description, category_id) VALUES (%s, %s, %s)"
        self.execute_query(query, product_data, many=True)
        print(f"Generated {len(product_data)} products")
    
    def generate_prices(self, product_count=500):
        """Generate price data for products"""
        print(f"Generating prices for {product_count} products...")
        
        price_data = []
        for product_id in range(1, product_count + 1):
            price_data.append((
                product_id,
                round(random.uniform(9.99, 999.99), 2),
                fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = "INSERT INTO price (product_id, price, last_updated) VALUES (%s, %s, %s)"
        self.execute_query(query, price_data, many=True)
        print(f"Generated {len(price_data)} prices")
    
    def generate_inventory(self, product_count=500):
        """Generate inventory data"""
        print(f"Generating inventory for {product_count} products...")
        
        inventory_data = []
        for product_id in range(1, product_count + 1):
            inventory_data.append((
                product_id,
                random.randint(0, 1000),
                fake.date_time_between(start_date='-30d', end_date='now')
            ))
        
        query = "INSERT INTO inventory (product_id, quantity, last_updated) VALUES (%s, %s, %s)"
        self.execute_query(query, inventory_data, many=True)
        print(f"Generated {len(inventory_data)} inventory records")
    
    def generate_orders(self, count=2000):
        """Generate order data"""
        print(f"Generating {count} orders...")
        
        order_data = []
        for order_id in range(1, count + 1):
            customer_id = random.randint(1, 1500)  # Ensure valid customer ID
            seller_id = random.randint(1, 100)     # Ensure valid seller ID
            total_quantity = random.randint(1, 10)
            total_amount = random.randint(50, 5000)
            
            order_data.append((
                order_id,
                customer_id,
                total_quantity,
                total_amount,
                fake.date_time_between(start_date='-2y', end_date='now'),
                seller_id
            ))
        
        query = """INSERT INTO orders 
                   (order_id, customer_id, total_quantity, total_amount, order_date, seller_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, order_data, many=True)
        print(f"Generated {len(order_data)} orders")
    
    def generate_orderitems(self, count=3000):
        """Generate order items data"""
        print(f"Generating {count} order items...")
        
        orderitem_data = []
        for _ in range(count):
            order_id = random.randint(1, 2000)     # Ensure valid order ID
            product_id = random.randint(1, 500)    # Ensure valid product ID
            customer_id = random.randint(1, 1500)  # Ensure valid customer ID
            seller_id = random.randint(1, 100)     # Ensure valid seller ID
            quantity = random.randint(1, 5)
            total_amount = random.randint(20, 1000)
            
            orderitem_data.append((
                order_id,
                product_id,
                customer_id,
                seller_id,
                quantity,
                total_amount
            ))
        
        query = """INSERT INTO orderitems 
                   (order_id, product_id, customer_id, seller_id, quantity, total_amount) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, orderitem_data, many=True)
        print(f"Generated {len(orderitem_data)} order items")
    
    def generate_shipping(self, count=1500):
        """Generate shipping data"""
        print(f"Generating {count} shipping records...")
        
        statuses = ['shipped', 'pending', 'delivered', 'cancelled']
        shipping_data = []
        
        for _ in range(count):
            order_id = random.randint(1, 2000)  # Ensure valid order ID
            shipping_date = fake.date_between(start_date='-2y', end_date='now')
            status = random.choice(statuses)
            
            # Delivery date only if shipped or delivered
            delivery_date = None
            if status in ['shipped', 'delivered']:
                delivery_date = fake.date_between(start_date=shipping_date, end_date='now')
            
            shipping_data.append((
                order_id,
                shipping_date,
                status,
                delivery_date,
                fake.street_address()[:200],
                fake.city(),
                fake.state(),
                fake.postcode(),
                fake.country()
            ))
        
        query = """INSERT INTO shipping 
                   (order_id, shipping_date, shipping_status, delivery_date, shipping_addresss, city, state, postalcode, country) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, shipping_data, many=True)
        print(f"Generated {len(shipping_data)} shipping records")
    
    def generate_logs(self, count=500):
        """Generate log data"""
        print(f"Generating {count} log records...")
        
        actions = ['INSERT', 'UPDATE', 'DELETE']
        tables = ['customers', 'orders', 'products', 'inventory', 'employees']
        columns = ['name', 'email', 'price', 'quantity', 'status', 'date']
        
        log_data = []
        for _ in range(count):
            log_data.append((
                random.choice(actions),
                fake.user_name(),
                random.choice(tables),
                random.choice(columns),
                fake.word(),
                fake.word(),
                fake.date_time_between(start_date='-1y', end_date='now')
            ))
        
        query = """INSERT INTO log 
                   (action, changed_by, on_table, on_column, old_value, new_value, time) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        self.execute_query(query, log_data, many=True)
        print(f"Generated {len(log_data)} log records")

    def generate_all_data(self):
        """Generate all sample data"""
        if not self.connect():
            print("Failed to connect to database")
            return
        
        try:
            print("Starting data generation...")
            print("=" * 50)
            
            # Clear existing data
            self.clear_tables()
            
            # Generate data in dependency order
            self.generate_categories(50)
            self.generate_customers(1500)
            self.generate_employees(100)
            self.generate_products(1000)
            self.generate_prices(1000)
            self.generate_inventory(1000)
            self.generate_orders(2000)
            self.generate_orderitems(5000)
            self.generate_shipping(2000)
            # self.generate_logs(500)
            
            print("=" * 50)
            print("Data generation complete!")
            
        except Exception as e:
            print(f"Error during data generation: {e}")
        finally:
            self.disconnect()

if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate_all_data()

