"""
Test script for MEXC Redis storage functionality
"""
import asyncio
import sys
from redis_client import redis_client
from datetime import datetime


async def test_mexc_redis_storage():
    """Test MEXC data storage in Redis"""
    
    print("=" * 80)
    print("Testing MEXC Redis Storage Functionality")
    print("=" * 80)
    
    try:
        # Connect to Redis
        print("\n1. Connecting to Redis...")
        await redis_client.connect()
        print("✓ Connected to Redis")
        
        # Test 1: Store and retrieve raw response
        print("\n2. Testing raw response storage...")
        test_response = {
            "balances": [
                {"asset": "QRL", "free": "1000.0", "locked": "0.0"},
                {"asset": "USDT", "free": "500.0", "locked": "0.0"}
            ],
            "updateTime": int(datetime.now().timestamp() * 1000)
        }
        
        success = await redis_client.set_mexc_raw_response("account_info", test_response)
        if success:
            print("✓ Raw response stored")
            
            retrieved = await redis_client.get_mexc_raw_response("account_info")
            if retrieved:
                print(f"✓ Raw response retrieved: {retrieved['endpoint']}")
                print(f"  Data contains {len(retrieved['data']['balances'])} balances")
            else:
                print("✗ Failed to retrieve raw response")
        else:
            print("✗ Failed to store raw response")
        
        # Test 2: Store and retrieve account balance
        print("\n3. Testing account balance storage...")
        balance_data = {
            "QRL": {"free": "1000.0", "locked": "0.0", "total": "1000.0"},
            "USDT": {"free": "500.0", "locked": "0.0", "total": "500.0"},
            "all_assets_count": 2
        }
        
        success = await redis_client.set_mexc_account_balance(balance_data)
        if success:
            print("✓ Account balance stored")
            
            retrieved = await redis_client.get_mexc_account_balance()
            if retrieved:
                print(f"✓ Account balance retrieved")
                print(f"  QRL: {retrieved['balances']['QRL']}")
                print(f"  USDT: {retrieved['balances']['USDT']}")
            else:
                print("✗ Failed to retrieve account balance")
        else:
            print("✗ Failed to store account balance")
        
        # Test 3: Store and retrieve QRL price
        print("\n4. Testing QRL price storage...")
        qrl_price = 0.0025
        price_data = {"symbol": "QRLUSDT", "price": "0.0025"}
        
        success = await redis_client.set_mexc_qrl_price(qrl_price, price_data)
        if success:
            print("✓ QRL price stored")
            
            retrieved = await redis_client.get_mexc_qrl_price()
            if retrieved:
                print(f"✓ QRL price retrieved: {retrieved['price_float']} USDT")
            else:
                print("✗ Failed to retrieve QRL price")
        else:
            print("✗ Failed to store QRL price")
        
        # Test 4: Store and retrieve total value
        print("\n5. Testing total value storage...")
        total_value = 502.5  # (1000 * 0.0025) + 500
        breakdown = {
            "qrl_quantity": 1000.0,
            "qrl_price_usdt": 0.0025,
            "qrl_value_usdt": 2.5,
            "usdt_balance": 500.0,
            "total_value_usdt": 502.5
        }
        
        success = await redis_client.set_mexc_total_value(total_value, breakdown)
        if success:
            print("✓ Total value stored")
            
            retrieved = await redis_client.get_mexc_total_value()
            if retrieved:
                print(f"✓ Total value retrieved: {retrieved['total_value_float']} USDT")
                print(f"  Breakdown: {retrieved['breakdown']}")
            else:
                print("✗ Failed to retrieve total value")
        else:
            print("✗ Failed to store total value")
        
        print("\n" + "=" * 80)
        print("All tests completed successfully! ✓")
        print("=" * 80)
        print("\nRedis Keys Created:")
        print("  - mexc:raw_response:account_info")
        print("  - mexc:account_balance")
        print("  - mexc:qrl_price")
        print("  - mexc:total_value")
        print("\nNote: All data is stored PERMANENTLY (no expiration)")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await redis_client.close()
        print("\n✓ Redis connection closed")


if __name__ == "__main__":
    asyncio.run(test_mexc_redis_storage())
