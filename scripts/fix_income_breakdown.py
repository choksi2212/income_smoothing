"""
Fix Income Breakdown page by ensuring all users have income sources
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import User, IncomeSource
from app.ml_service_enhanced import EnhancedMLService

def fix_income_sources():
    """Ensure all users have income sources"""
    print("=" * 60)
    print("FIXING INCOME BREAKDOWN - Generating Income Sources")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        print(f"\n✅ Found {len(users)} users")
        
        fixed_count = 0
        already_ok = 0
        
        ml_service = EnhancedMLService(db)
        
        for user in users:
            user_id = str(user.user_id)
            
            # Check if user has income sources
            existing_sources = db.query(IncomeSource).filter(
                IncomeSource.user_id == user.user_id
            ).count()
            
            if existing_sources == 0:
                print(f"\n  Fixing {user.email}...")
                try:
                    ml_service.update_income_sources(user_id)
                    fixed_count += 1
                    print(f"    ✅ Generated income sources")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            else:
                already_ok += 1
        
        print(f"\n" + "=" * 60)
        print(f"SUMMARY")
        print(f"=" * 60)
        print(f"  ✅ Already had sources: {already_ok}")
        print(f"  ✅ Fixed: {fixed_count}")
        print(f"  ✅ Total: {len(users)}")
        
        # Verify
        print(f"\n" + "=" * 60)
        print(f"VERIFICATION")
        print(f"=" * 60)
        
        for user in users[:5]:  # Show first 5
            sources = db.query(IncomeSource).filter(
                IncomeSource.user_id == user.user_id
            ).all()
            
            print(f"\n  {user.email}:")
            print(f"    Sources: {len(sources)}")
            for source in sources[:3]:
                print(f"      - {source.source_name}: {float(source.contribution_pct):.1f}%")
        
        print(f"\n" + "=" * 60)
        print(f"✅ INCOME BREAKDOWN FIXED!")
        print(f"=" * 60)
    
    finally:
        db.close()


if __name__ == "__main__":
    fix_income_sources()
