"""
Check if the scenario system is properly installed.
"""

import sys
from app.database import SessionLocal
from app.models.scenario import Scenario
from app.config import settings


def check_installation():
    """Check if scenario system is installed correctly."""

    print("=" * 60)
    print("Scenario System Installation Check")
    print("=" * 60)

    # Check 1: Database connection
    print("\n1. Checking database connection...")
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        print("   ✓ Database connection OK")
    except Exception as e:
        print(f"   ✗ Database connection failed: {e}")
        return False

    # Check 2: Scenarios table exists
    print("\n2. Checking scenarios table...")
    try:
        scenarios = db.query(Scenario).all()
        print(f"   ✓ Scenarios table exists")
        print(f"   ✓ Found {len(scenarios)} scenarios")
    except Exception as e:
        print(f"   ✗ Scenarios table error: {e}")
        return False

    # Check 3: Initial scenarios seeded
    print("\n3. Checking initial scenarios...")
    if len(scenarios) >= 4:
        print("   ✓ Initial scenarios are seeded")
        for s in scenarios:
            print(f"      - {s.name_ru}")
    else:
        print(f"   ⚠ Expected 4 scenarios, found {len(scenarios)}")
        print("   → Run: python init_db.py")

    # Check 4: OpenAI API key
    print("\n4. Checking OpenAI API key...")
    if settings.openai_api_key:
        key_preview = settings.openai_api_key[:15] + "..." if len(settings.openai_api_key) > 15 else settings.openai_api_key
        print(f"   ✓ OpenAI API key configured: {key_preview}")
    else:
        print("   ⚠ OpenAI API key not configured")
        print("   → Add OPENAI_API_KEY to backend/.env")

    # Check 5: Models can be imported
    print("\n5. Checking models...")
    try:
        from app.models.scenario import Scenario
        from app.services.scenario_manager import ScenarioManager
        from app.services.name_generator import NameGenerator
        from app.services.review_generator import ReviewGenerator
        print("   ✓ All models can be imported")
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        return False

    # Check 6: Routes registered
    print("\n6. Checking routes...")
    try:
        from app.routes import scenarios, generators
        print("   ✓ New routes are registered")
    except ImportError as e:
        print(f"   ✗ Routes error: {e}")
        return False

    db.close()

    print("\n" + "=" * 60)
    print("✓ Installation check completed successfully!")
    print("=" * 60)

    print("\nNext steps:")
    print("1. Start backend: uvicorn app.main:app --reload")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open: http://localhost:3000/generate")

    return True


if __name__ == "__main__":
    try:
        success = check_installation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
