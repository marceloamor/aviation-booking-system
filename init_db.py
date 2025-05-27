#!/usr/bin/env python
from src.utils.seed_db import seed_database

if __name__ == "__main__":
    print("Initializing the database...")
    seed_database()
    print("Database initialization completed successfully!") 