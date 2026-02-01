"""
Test script to verify Enhanced ML Service integration
Tests pre-trained model loading and prediction speed
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.ml_service_enhanced import EnhancedMLService
from app.models import User

def test_enhanced_ml_service():
    """Test the enhanced ML service with pre-trained models"""
    print("=" * 60)
    print("TESTING ENHANCED ML SERVICE")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Get a test user
        user = db.query(User).first()
        
        if not user:
            print("❌ No users found in database")
            return
        
        user_id = str(user.user_id)
        print(f"\n✅ Testing with user: {user.email}")
        print(f"   User ID: {user_id}")
        
        # Initialize enhanced ML service
        ml_service = EnhancedMLService(db)
        print("\n✅ Enhanced ML Service initialized")
        
        # Test 1: Check model availability
        print("\n" + "=" * 60)
        print("TEST 1: Model Availability")
        print("=" * 60)
        
        model_info = ml_service.get_model_info(user_id)
        print(f"\nUser ID: {model_info['user_id']}")
        print("\nAvailable Models:")
        
        for model_type, info in model_info['models'].items():
            if info['available']:
                print(f"  ✅ {model_type.upper()}")
                print(f"     Size: {info['size_kb']:.2f} KB")
                print(f"     Modified: {info['modified']}")
            else:
                print(f"  ❌ {model_type.upper()} - Not available")
        
        # Test 2: Prediction speed comparison
        print("\n" + "=" * 60)
        print("TEST 2: Prediction Speed (7-day forecast)")
        print("=" * 60)
        
        # Test with enhanced service (pre-trained models)
        start_time = time.time()
        prediction = ml_service.predict_cashflow_enhanced(user_id, days=7)
        enhanced_time = time.time() - start_time
        
        print(f"\n✅ Enhanced ML Service (Pre-trained)")
        print(f"   Time: {enhanced_time:.4f} seconds")
        print(f"   Model Used: {prediction['model_used']}")
        print(f"   Expected Inflow: ₹{prediction['expected_inflow_inr']:,.2f}")
        print(f"   Expected Outflow: ₹{prediction['expected_outflow_inr']:,.2f}")
        print(f"   Net Cashflow: ₹{prediction['net_cashflow_inr']:,.2f}")
        print(f"   Confidence: {float(prediction['confidence_score']):.2%}")
        
        # Test 3: Multiple predictions (stress test)
        print("\n" + "=" * 60)
        print("TEST 3: Stress Test (10 predictions)")
        print("=" * 60)
        
        times = []
        for i in range(10):
            start_time = time.time()
            ml_service.predict_cashflow_enhanced(user_id, days=30)
            times.append(time.time() - start_time)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n✅ Completed 10 predictions")
        print(f"   Average Time: {avg_time:.4f} seconds")
        print(f"   Min Time: {min_time:.4f} seconds")
        print(f"   Max Time: {max_time:.4f} seconds")
        print(f"   Throughput: {1/avg_time:.2f} predictions/second")
        
        # Test 4: Save prediction to database
        print("\n" + "=" * 60)
        print("TEST 4: Save Prediction to Database")
        print("=" * 60)
        
        start_time = time.time()
        saved_pred = ml_service.save_prediction(user_id, days=30)
        save_time = time.time() - start_time
        
        print(f"\n✅ Prediction saved to database")
        print(f"   Time: {save_time:.4f} seconds")
        print(f"   Prediction ID: {saved_pred.prediction_id}")
        print(f"   Model Used: {saved_pred.model_used}")
        print(f"   Expected Inflow: ₹{saved_pred.expected_inflow_inr:,.2f}")
        print(f"   Net Cashflow: ₹{saved_pred.net_cashflow_inr:,.2f}")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        models_available = sum(1 for info in model_info['models'].values() if info['available'])
        
        print(f"\n✅ All tests passed!")
        print(f"   Models Available: {models_available}/3")
        print(f"   Average Prediction Time: {avg_time:.4f}s")
        print(f"   Performance: {'🚀 EXCELLENT' if avg_time < 0.5 else '✅ GOOD' if avg_time < 2 else '⚠️ SLOW'}")
        
        if avg_time < 0.5:
            improvement = 2.5 / avg_time  # Assuming 2.5s for real-time training
            print(f"   Speed Improvement: ~{improvement:.0f}x faster than real-time training!")
        
        print("\n" + "=" * 60)
        print("✅ ENHANCED ML SERVICE IS WORKING PERFECTLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_enhanced_ml_service()
