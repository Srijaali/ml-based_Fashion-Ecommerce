import os

print("=" * 60)
print("Setting up PostgreSQL Connection")
print("=" * 60)

# Get PostgreSQL credentials
host = input("PostgreSQL Host (default: localhost): ").strip() or "localhost"
port = input("PostgreSQL Port (default: 5432): ").strip() or "5432"
database = input("Database name (default: fashion_db): ").strip() or "fashion_db"
user = input("PostgreSQL user (default: postgres): ").strip() or "postgres"
password = input("PostgreSQL password: ").strip()

if not password:
    print("❌ Password cannot be empty!")
    exit(1)

# Create .env file
env_content = f"""# PostgreSQL Connection
DB_HOST={host}
DB_PORT={port}
DB_NAME={database}
DB_USER={user}
DB_PASSWORD={password}
DB_SCHEMA=niche_data

# Optional
DEBUG=True
LOG_LEVEL=INFO
"""

# Write to .env
with open(".env", "w") as f:
    f.write(env_content)

print("\n✅ .env file created successfully!")
print(f"\nConnection Details:")
print(f"  Host: {host}")
print(f"  Port: {port}")
print(f"  Database: {database}")
print(f"  User: {user}")
print(f"\n🔒 Password is stored in .env (do NOT commit to git!)")