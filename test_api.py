import requests
import json
import time

def test_api():
    base_url = "http://127.0.0.1:5000"
    
    # Wait for the server to start (it should be fast)
    time.sleep(2)
    
    print("="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    payload = {
        "TV": 50.0,
        "Radio": 20.0,
        "Social Media": 5.0
    }
    
    print(f"\n[Scénario de test] Budget TV: 50, Radio: 20, Social: 5")
    
    # 1. Test Performance Endpoint
    print("\n--- 1. POST /predict/performance ---")
    try:
        response = requests.post(f"{base_url}/predict/performance", json=payload)
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
        
    # 2. Test ROI Endpoint
    print("\n--- 2. POST /predict/roi ---")
    try:
        response = requests.post(f"{base_url}/predict/roi", json=payload)
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")
        
    # 3. Test SHAP Endpoint
    print("\n--- 3. POST /predict/shap_impact ---")
    try:
        response = requests.post(f"{base_url}/predict/shap_impact", json=payload)
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
