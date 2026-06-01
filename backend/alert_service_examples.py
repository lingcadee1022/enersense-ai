"""
Alert Service Usage Examples and Testing

This file demonstrates how to use the EnerSense AI Alert Service
with example scenarios and API calls.
"""

import requests
import json
from datetime import datetime

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
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


# ==================== EXAMPLE 1: GET LATEST ALERT ====================

def example_get_latest_alert():
    """
    Example: Get the latest alert for a device
    
    GET /api/v1/alerts/latest?device_id=esp32_01
    """
    print_section("Example 1: Get Latest Alert")
    
    try:
        url = f"{BASE_URL}/alerts/latest"
        params = {"device_id": DEVICE_ID}
        
        print_info(f"GET {url}?device_id={DEVICE_ID}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Response received")
            print(json.dumps(data, indent=2))
            
            if data.get("has_active_alert"):
                alert = data.get("alert_data")
                print_info(f"Alert Level: {alert.get('level')}")
                print_info(f"Alert Type: {alert.get('type')}")
                print_info(f"Current Power: {alert.get('current_power')}W")
                print_info(f"Average Power: {alert.get('avg_power')}W")
            else:
                print_info("No active alerts for device")
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


# ==================== EXAMPLE 2: GET ALERT HISTORY ====================

def example_get_alert_history():
    """
    Example: Get alert history with filters
    
    GET /api/v1/alerts/history?device_id=esp32_01&hours=24&limit=10
    GET /api/v1/alerts/history?device_id=esp32_01&level=critical&limit=5
    """
    print_section("Example 2: Get Alert History")
    
    # Query 1: Last 24 hours
    try:
        url = f"{BASE_URL}/alerts/history"
        params = {
            "device_id": DEVICE_ID,
            "hours": 24,
            "limit": 10
        }
        
        print_info(f"Query 1: Alerts from last 24 hours")
        print_info(f"GET {url}?device_id={DEVICE_ID}&hours=24&limit=10")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            alerts = response.json()
            print_success(f"Retrieved {len(alerts)} alerts")
            
            for i, alert in enumerate(alerts[:3], 1):  # Show first 3
                print(f"\n  Alert {i}:")
                print(f"    - Type: {alert.get('type')}")
                print(f"    - Level: {alert.get('level')}")
                print(f"    - Power: {alert.get('current_power')}W")
                print(f"    - Time: {alert.get('timestamp')}")
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Query 2: Only critical alerts
    try:
        url = f"{BASE_URL}/alerts/history"
        params = {
            "device_id": DEVICE_ID,
            "level": "critical",
            "limit": 5
        }
        
        print_info(f"\nQuery 2: Critical alerts only")
        print_info(f"GET {url}?device_id={DEVICE_ID}&level=critical&limit=5")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            alerts = response.json()
            print_success(f"Retrieved {len(alerts)} critical alerts")
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


# ==================== EXAMPLE 3: GET CRITICAL ALERTS ====================

def example_get_critical_alerts():
    """
    Example: Get only critical alerts
    
    GET /api/v1/alerts/critical?device_id=esp32_01&limit=10
    """
    print_section("Example 3: Get Critical Alerts")
    
    try:
        url = f"{BASE_URL}/alerts/critical"
        params = {
            "device_id": DEVICE_ID,
            "limit": 10
        }
        
        print_info(f"GET {url}?device_id={DEVICE_ID}&limit=10")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            alerts = response.json()
            print_success(f"Retrieved {len(alerts)} critical alerts")
            
            if alerts:
                print_info("Critical alerts summary:")
                for alert in alerts[:5]:  # Show first 5
                    print(f"  - {alert.get('type')}: {alert.get('message')}")
            else:
                print_info("No critical alerts found")
        else:
            print_error(f"HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


# ==================== EXAMPLE 4: ALERT GENERATION (Manual) ====================

def example_generate_alert_manual():
    """
    Example: Manually generate an alert using the AlertService
    
    This would be called internally when new sensor data arrives.
    """
    print_section("Example 4: Generate Alert (Internal)")
    
    print_info("In production, alerts are generated automatically when:")
    print("  1. New sensor data arrives via POST /sensor-data")
    print("  2. AlertService.generate_alert() is called")
    print("  3. Alert conditions are detected (HIGH_USAGE, CRITICAL_USAGE, SUDDEN_SPIKE)")
    
    print_info("\nExample alert generation code:")
    print("""
    from services.alert_service import AlertService
    
    # Generate alert for current sensor reading
    alert = AlertService.generate_alert(
        device_id="esp32_01",
        current_power=1800.0,          # Current reading in Watts
        previous_power=1200.0,         # Previous reading (for spike detection)
        hours_window=24                # Look at last 24 hours of data
    )
    
    # Response contains:
    {
        "alert": true,
        "level": "warning",            # "warning" or "critical"
        "type": "HIGH_USAGE",          # "HIGH_USAGE", "CRITICAL_USAGE", "SUDDEN_SPIKE"
        "message": "WARNING: Energy consumption is 1800W...",
        "current_power": 1800.0,
        "avg_power": 900.5,
        "std_power": 150.25,
        "timestamp": "2026-05-31T15:30:00Z",
        "threshold_exceeded": 600.0    # Amount over threshold
    }
    """)


# ==================== EXAMPLE 5: ALERT CONDITIONS EXPLAINED ====================

def example_alert_conditions():
    """
    Example: Understand alert detection conditions
    """
    print_section("Example 5: Alert Conditions Explained")
    
    print_info("Alert Detection Logic:")
    print("""
    1. HIGH_USAGE
       Condition: power > avg_power + 2 * std_power
       Priority: WARNING level
       Example: If average=800W and std=150W
                Alert triggers when power > 800 + 2*150 = 1100W
    
    2. CRITICAL_USAGE (Higher Priority)
       Condition: power > avg_power + 3 * std_power
       Priority: CRITICAL level
       Example: If average=800W and std=150W
                Alert triggers when power > 800 + 3*150 = 1250W
       Note: Checked FIRST, overrides HIGH_USAGE if triggered
    
    3. SUDDEN_SPIKE
       Condition: current_power > previous_power * 1.5
       Priority: WARNING level
       Example: If previous reading was 800W
                Alert triggers when power > 800 * 1.5 = 1200W
       Note: Requires previous_power to be available
    """)
    
    print_info("\nExample Scenario:")
    print("""
    Device Profile (from 24 hours of data):
    - Average Power: 800W
    - Standard Deviation: 150W
    
    Thresholds:
    - HIGH_USAGE: 1100W (WARNING)
    - CRITICAL_USAGE: 1250W (CRITICAL)
    - SUDDEN_SPIKE: 1.5x previous reading (WARNING)
    
    Incoming Readings:
    1. 900W → No alert (within range)
    2. 1050W → No alert (below HIGH_USAGE threshold)
    3. 1200W → WARNING: HIGH_USAGE (exceeds 1100W)
    4. 1300W → CRITICAL: CRITICAL_USAGE (exceeds 1250W)
    5. 600W then 1000W → WARNING: SUDDEN_SPIKE (>600*1.5)
    """)


# ==================== EXAMPLE 6: DATABASE INTEGRATION ====================

def example_database_integration():
    """
    Example: Understand how alerts are stored in MongoDB
    """
    print_section("Example 6: Database Integration")
    
    print_info("MongoDB Collections:")
    print("""
    Collection: alerts
    
    Document Schema:
    {
        "_id": ObjectId,
        "device_id": "esp32_01",
        "alert": true,
        "level": "warning",           // or "critical"
        "type": "HIGH_USAGE",         // or "CRITICAL_USAGE", "SUDDEN_SPIKE"
        "message": "WARNING: Energy consumption...",
        "current_power": 1500.0,
        "avg_power": 800.5,
        "std_power": 150.25,
        "timestamp": "2026-05-31T15:30:00Z",
        "threshold_exceeded": 300.0,  // Optional: amount over threshold
        "spike_percentage": null,     // Optional: % increase for spikes
        "inserted_at": "2026-05-31T15:30:00Z"
    }
    
    Indexes Created:
    - device_id
    - timestamp
    - level
    - (device_id, timestamp) - For fast recent alerts queries
    - (device_id, level, timestamp) - For filtering by level
    """)
    
    print_info("\nQueries Performed:")
    print("""
    1. Get latest alert:
       db.alerts.findOne(
           {"device_id": "esp32_01"},
           {sort: [["timestamp", -1]]}
       )
    
    2. Get alerts by level:
       db.alerts.find(
           {"device_id": "esp32_01", "level": "critical"},
           {sort: [["timestamp", -1]]}
       ).limit(10)
    
    3. Get recent alerts (last 24 hours):
       db.alerts.find({
           "device_id": "esp32_01",
           "timestamp": {$gte: "2026-05-30T15:30:00Z"}
       }).sort({timestamp: -1}).limit(50)
    """)


# ==================== EXAMPLE 7: RESPONSE EXAMPLES ====================

def example_response_formats():
    """
    Example: Different response formats
    """
    print_section("Example 7: Response Formats")
    
    print_info("GET /alerts/latest - Latest Alert Response:")
    print(json.dumps({
        "device_id": "esp32_01",
        "has_active_alert": True,
        "alert_data": {
            "alert": True,
            "level": "warning",
            "type": "HIGH_USAGE",
            "message": "WARNING: Energy consumption is 1500W, exceeding threshold of 1200W",
            "current_power": 1500.0,
            "avg_power": 800.5,
            "std_power": 150.25,
            "timestamp": "2026-05-31T15:30:00Z",
            "threshold_exceeded": 300.0,
            "spike_percentage": None
        }
    }, indent=2))
    
    print_info("\nGET /alerts/history - Alert History Response:")
    print(json.dumps([
        {
            "alert": True,
            "level": "critical",
            "type": "CRITICAL_USAGE",
            "message": "CRITICAL: Energy consumption is 2500W, exceeding threshold of 2000W",
            "current_power": 2500.0,
            "avg_power": 800.5,
            "std_power": 150.25,
            "timestamp": "2026-05-31T15:45:00Z",
            "threshold_exceeded": 500.0,
            "spike_percentage": None
        },
        {
            "alert": True,
            "level": "warning",
            "type": "SUDDEN_SPIKE",
            "message": "WARNING: Sudden power spike detected. Power increased from 1200W to 1900W (58% increase)",
            "current_power": 1900.0,
            "avg_power": 800.5,
            "std_power": 150.25,
            "timestamp": "2026-05-31T15:30:00Z",
            "threshold_exceeded": None,
            "spike_percentage": 58.3
        }
    ], indent=2))


# ==================== MAIN ====================

def main():
    """Run all examples"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{'EnerSense AI - Alert Service Examples':^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    print_info("This script demonstrates the Alert Service API")
    print_info("Ensure the backend is running: python main.py")
    print_info(f"Backend URL: {BASE_URL}\n")
    
    # Non-network examples (always work)
    example_alert_conditions()
    example_database_integration()
    example_generate_alert_manual()
    example_response_formats()
    
    # Network examples (require running backend)
    try:
        print_section("Testing Backend Connection")
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        
        if response.status_code == 200:
            print_success("Backend is running!")
            print_info("Running API endpoint examples...\n")
            
            example_get_latest_alert()
            example_get_alert_history()
            example_get_critical_alerts()
        else:
            print_error(f"Backend returned: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BASE_URL}")
        print_info("Start the backend with: cd backend && python main.py")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    print(f"\n{BLUE}{'='*70}{RESET}\n")


if __name__ == "__main__":
    main()
