from database.db import init_db, seed_db

print("Initializing database...")
init_db()
print("Seeding database...")
seed_db()
print("Database setup complete!")
