import requests
import json
import os
import sys

print("=== Testing Audio Preprocessor API ===")
print(f"Current directory: {os.getcwd()}")
print(f"Test file exists: {os.path.exists('test_sine.wav')}")

url = 'http://localhost:5004/preprocess'

try:
    # Read the file
    with open('test_sine.wav', 'rb') as f:
        file_content = f.read()
    
    print(f"\nFile size: {len(file_content)} bytes")
    
    # Prepare the request
    files = {'file': ('test_sine.wav', file_content, 'audio/wav')}
    data = {
        'sample_rate': '22050',
        'remove_silence': 'true',
        'normalize_loudness': 'true',
        'target_lufs': '-23.0'
    }
    
    print("\nSending POST request to /preprocess...")
    
    # Send request with verbose output
    response = requests.post(url, files=files, data=data, timeout=120)
    
    print(f"\nResponse Status Code: {response.status_code}")
    print(f"Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n=== SUCCESS ===")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n=== ERROR ===")
        print(f"Response text: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n=== TIMEOUT ===")
    print("Request timed out after 120 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"\n=== CONNECTION ERROR ===")
    print(f"Cannot connect to {url}")
    print(f"Error: {e}")
except Exception as e:
    print(f"\n=== EXCEPTION ===")
    print(f"Type: {type(e).__name__}")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test completed ===")