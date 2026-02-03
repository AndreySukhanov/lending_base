"""
Database initialization script.
Creates all tables and seeds initial data.
"""

from app.database import engine, SessionLocal
from app.models import Base
from app.seeds.initial_scenarios import seed_scenarios


def init_db():
    """Initialize database with tables and seed data."""
    print("Creating database tables...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")

    # Seed initial data
    print("\nSeeding initial data...")
    db = SessionLocal()
    try:
        seed_scenarios(db)
        print("✓ Initial data seeded successfully")
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

    print("\n✓ Database initialization completed!")


if __name__ == "__main__":
    init_db()
