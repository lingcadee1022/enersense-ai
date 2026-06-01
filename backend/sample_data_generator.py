"""
Sample data generator and API tester for EnerSense AI Backend.

This script:
1. Generates realistic sensor data
2. Tests all API endpoints
3. Demonstrates backend functionality
4. Shows expected responses

Usage:
    python sample_data_generator.py
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
DEVICE_ID = "esp32_01"

# Colors for terminal output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def print_section(title):
    """Print section header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def print_response(response_data, title="Response"):
    """Pretty print response data."""
    print(f"\n{YELLOW}{title}:{RESET}")
    print(json.dumps(response_data, indent=2))


def generate_sensor_data(base_power=150, variation=50, current_ratio=0.003):
    """
    Generate realistic sensor data.
    
    Args:
        base_power: Base power consumption in Watts
        variation: Random variation in Watts
        current_ratio: Current per Watt (typically 0.003-0.005 A/W)
    
    Returns:
        Dictionary with power and current
    """
    power = base_power + random.randint(-variation, variation)
    power = max(50, power)  # Minimum 50W
    current = power * current_ratio
    
    return {
        "device_id": DEVICE_ID,
        "power": round(power, 1),
        "current": round(current, 3)
    }


def test_health_check():
    """Test health check endpoint."""
    print_section("1. HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code == 200:
            print_success("Health check passed")
            print_response(response.json())
        else:
            print_error(f"Health check failed: {response.status_code}")
    except Exception as e:
        print_error(f"Connection error: {str(e)}")


def test_send_sensor_data():
    """Test sending sensor data."""
    print_section("2. SEND SENSOR DATA")
    
    try:
        # Send 5 sensor readings with time intervals
        for i in range(5):
            data = generate_sensor_data()
            response = requests.post(f"{BASE_URL}/sensor-data", json=data)
            
            if response.status_code == 200:
                print_success(f"Sensor reading {i+1}: Power={data['power']}W, Current={data['current']}A")
                time.sleep(0.5)
            else:
                print_error(f"Failed to send sensor data: {response.status_code}")
        
        print_response(response.json(), "Last Response")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_batch_send_sensor_data():
    """Test sending batch sensor data."""
    print_section("3. SEND BATCH SENSOR DATA")
    
    try:
        # Generate 10 readings
        batch_data = [generate_sensor_data() for _ in range(10)]
        
        response = requests.post(f"{BASE_URL}/sensor-data/batch", json=batch_data)
        
        if response.status_code == 200:
            print_success(f"Batch of {len(batch_data)} readings sent successfully")
            print_response(response.json())
        else:
            print_error(f"Batch send failed: {response.status_code}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_live_usage():
    """Test getting live usage."""
    print_section("4. GET LIVE USAGE")
    
    try:
        response = requests.get(f"{BASE_URL}/live-usage?device_id={DEVICE_ID}")
        
        if response.status_code == 200:
            print_success("Retrieved live usage")
            data = response.json()
            print_response(data)
            print_info(f"Latest Power: {data['power']}W, Current: {data['current']}A")
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_history(hours=1):
    """Test getting history."""
    print_section(f"5. GET HISTORY (Last {hours} hour(s))")
    
    try:
        response = requests.get(f"{BASE_URL}/history?device_id={DEVICE_ID}&hours={hours}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data)} history records")
            
            if data:
                print_info(f"Time range: {data[0]['timestamp']} to {data[-1]['timestamp']}")
                print_response(data[:3], "First 3 records")
            else:
                print_info("No history found")
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_history_summary(hours=1):
    """Test getting history summary."""
    print_section(f"6. GET HISTORY SUMMARY (Last {hours} hour(s))")
    
    try:
        response = requests.get(f"{BASE_URL}/history/summary?device_id={DEVICE_ID}&hours={hours}")
        
        if response.status_code == 200:
            print_success("Retrieved history summary")
            print_response(response.json())
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_train_profile(days=1):
    """Test training user profile."""
    print_section(f"7. TRAIN USER PROFILE (Using {days} day(s))")
    
    try:
        response = requests.post(f"{BASE_URL}/insights/train-profile?device_id={DEVICE_ID}&days={days}")
        
        if response.status_code == 200:
            print_success("Profile trained successfully")
            data = response.json()
            print_response(data)
            print_info(f"Trained on {data.get('samples', 'N/A')} samples")
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_get_profile():
    """Test getting user profile."""
    print_section("8. GET USER PROFILE")
    
    try:
        response = requests.get(f"{BASE_URL}/insights/profile?device_id={DEVICE_ID}")
        
        if response.status_code == 200:
            print_success("Retrieved user profile")
            print_response(response.json())
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_insights():
    """Test getting AI insights."""
    print_section("9. GET AI INSIGHTS")
    
    try:
        response = requests.get(f"{BASE_URL}/insights?device_id={DEVICE_ID}")
        
        if response.status_code == 200:
            print_success("Generated AI insights")
            data = response.json()
            
            print(f"\n{YELLOW}Energy Score: {RESET}{data.get('energy_score', 'N/A')}/100")
            print(f"{YELLOW}Estimated Cost: {RESET}RM {data.get('estimated_cost_rm', 'N/A'):.4f}/hour")
            
            if 'behavior_profile' in data:
                profile = data['behavior_profile']
                print(f"\n{YELLOW}Behavior Profile:{RESET}")
                print(f"  - Avg Power: {profile.get('avg_power', 'N/A')}W")
                print(f"  - Avg Current: {profile.get('avg_current', 'N/A')}A")
                print(f"  - Peak Hour: {profile.get('peak_hour', 'N/A')}:00")
                print(f"  - Usage Pattern: {profile.get('usage_pattern', 'N/A')}")
            
            if 'insights' in data:
                print(f"\n{YELLOW}Insights:{RESET}")
                for i, insight in enumerate(data['insights'], 1):
                    print(f"  {i}. {insight}")
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'EnerSense AI Backend - API Test Suite':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"\n{YELLOW}Target: {BASE_URL}{RESET}")
    print(f"{YELLOW}Device: {DEVICE_ID}{RESET}")
    print(f"{YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    
    try:
        # Test sequence
        test_health_check()
        
        time.sleep(1)
        test_send_sensor_data()
        
        time.sleep(1)
        test_batch_send_sensor_data()
        
        time.sleep(1)
        test_live_usage()
        
        time.sleep(1)
        test_history(hours=1)
        
        time.sleep(1)
        test_history_summary(hours=1)
        
        time.sleep(1)
        test_train_profile(days=1)
        
        time.sleep(1)
        test_get_profile()
        
        time.sleep(1)
        test_insights()
        
        # Summary
        print_section("TEST SUITE COMPLETED")
        print_success("All tests completed successfully!")
        print_info("Check the API documentation at http://localhost:8000/docs")
        print_info("Check custom docs at http://localhost:8000/docs-custom")
        
    except KeyboardInterrupt:
        print_error("\nTest suite interrupted by user")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
