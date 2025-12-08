import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get connection details
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
database = os.getenv('DB_NAME', 'fashion_db')
user = os.getenv('DB_USER', 'postgres')
password = os.getenv('DB_PASSWORD')

print("=" * 60)
print("Testing PostgreSQL Connection")
print("=" * 60)
print(f"\nConnection Details:")
print(f"  Host: {host}")
print(f"  Port: {port}")
print(f"  Database: {database}")
print(f"  User: {user}")
print(f"  Password: {'*' * len(password) if password else 'NOT SET'}")

try:
    # Attempt connection
    print("\n🔄 Attempting connection...")
    
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    
    # Get cursor
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    
    print("\n✅ Connection Successful!")
    print(f"\nPostgreSQL Version:")
    print(f"  {db_version[0]}")
    
    # List tables in niche_data schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'niche_data'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    if tables:
        print(f"\n✅ Found {len(tables)} tables in niche_data schema:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("\n⚠️ No tables found in niche_data schema")
        print("   You may need to run database setup scripts")
    
    # Close connections
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Connection Failed!")
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("  1. Check PostgreSQL is running")
    print("  2. Verify password in .env is correct")
    print("  3. Ensure database 'fashion_db' exists")
    print("  4. Check port 5432 is not blocked by firewall")

except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")