"""Test income sources API endpoint"""
import requests
import json
import time

time.sleep(3)  # Wait for server to start

# Login
print("Testing Income Sources API...")
print("=" * 60)

login_response = requests.post('http://localhost:8000/auth/login', data={
    'username': 'testuser1@example.com',
    'password': 'TestPass123'
})

print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get income sources
    response = requests.get('http://localhost:8000/features/income-sources', headers=headers)
    print(f"Income sources status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nFound {len(data)} income sources:")
        for source in data:
            print(f"  - {source['source_name']}: {source['contribution_pct']}%")
            print(f"    Avg monthly: ₹{source['avg_monthly_inr']}")
            print(f"    Stability: {source['stability_score']}")
    else:
        print(f"Error: {response.text}")
else:
    print(f"Login failed: {login_response.text}")
