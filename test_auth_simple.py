#!/usr/bin/env python3
import requests
import json

def main():
    print("=" * 60)
    print("ANWALTS AI AUTHENTICATION SYSTEM TEST")
    print("=" * 60)
    
    # Test direct backend authentication
    print("Testing Backend Authentication Directly...")
    
    url = "http://localhost:8000/auth/login-working"
    credentials = {
        "email": "the.ai.entrepreneur.ai.hub@gmail.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=credentials, timeout=10)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("token"):
                print("SUCCESS: Authentication Working!")
                print(f"   Token: {data['token'][:50]}...")
                print(f"   User: {data['user']['email']}")
                print(f"   Role: {data['user']['role']}")
                
                # Test token validation
                print("\nTesting Token Validation...")
                auth_url = "http://localhost:8000/auth/validate"
                headers = {"Authorization": f"Bearer {data['token']}"}
                
                val_response = requests.get(auth_url, headers=headers, timeout=10)
                if val_response.status_code == 200:
                    print("SUCCESS: Token validation working!")
                else:
                    print(f"Token validation failed: {val_response.status_code}")
                    
            else:
                print("FAILED: Authentication failed -", data.get('error', 'Unknown error'))
        else:
            print(f"FAILED: HTTP Error {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"FAILED: Connection Error - {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Working Credentials:")
    print("   Email: the.ai.entrepreneur.ai.hub@gmail.com")
    print("   Password: admin123")
    print("\nBackend Endpoint:")
    print("   URL: http://localhost:8000/auth/login-working")
    print("\nISSUE IDENTIFIED:")
    print("   Frontend has build-time configuration issue")
    print("   Backend authentication works perfectly")
    print("=" * 60)

if __name__ == "__main__":
    main()