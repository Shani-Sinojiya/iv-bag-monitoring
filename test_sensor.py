import requests
import time
import random
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/sensor"
SIMULATE_DURATION = 60  # seconds
UPDATE_INTERVAL = 1     # seconds


def simulate_iv_bag_depletion():
    """
    Simulate IV bag weight decreasing over time with some random variation
    """
    print("🏥 Starting IV Bag Sensor Simulation")
    print(f"Sending data to: {API_URL}")
    print(f"Duration: {SIMULATE_DURATION} seconds")
    print("-" * 50)

    # Starting weight (full IV bag - 1000ml = ~1000g plus bag weight ~100g)
    current_weight = 100

    start_time = time.time()

    while time.time() - start_time < SIMULATE_DURATION:
        try:
            # Simulate gradual weight decrease (IV dripping)
            # Decrease by 1-3 grams per second with some random variation
            weight_change = random.uniform(0.5, 2.5)
            current_weight -= weight_change

            # Add small random fluctuations to simulate sensor noise
            noise = random.uniform(-0.5, 0.5)
            measured_weight = max(0, int(current_weight + noise))

            # Send data to API
            response = requests.post(API_URL, json={"weight": measured_weight})

            if response.status_code == 200:
                result = response.json()
                timestamp = datetime.now().strftime("%H:%M:%S")
                status = result.get("status", "unknown")

                if status == "success":
                    print(
                        f"[{timestamp}] ✅ Weight: {measured_weight}g - Data recorded")
                elif status == "ignored":
                    print(
                        f"[{timestamp}] ⏭️  Weight: {measured_weight}g - No change, ignored")

                # Alert when getting low
                if measured_weight < 100:
                    print(
                        f"[{timestamp}] ⚠️  LOW WEIGHT ALERT: {measured_weight}g")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            print("Make sure FastAPI server is running on http://localhost:8000")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        # Wait before next reading
        time.sleep(UPDATE_INTERVAL)

        # Reset weight if it gets too low (simulate bag replacement)
        if current_weight <= 0:
            print("\n🔄 Simulating IV bag replacement...")
            current_weight = 1100
            time.sleep(3)  # Pause for bag replacement

    print("\n✅ Simulation completed!")
    print("You can now check the live dashboard at: http://localhost:8000/live")


def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing API Endpoints")
    print("-" * 30)

    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except:
        print("❌ Health endpoint: Server not responding")

    # Test sensor endpoint with sample data
    try:
        response = requests.post(API_URL, json={"weight": 750})
        if response.status_code == 200:
            print("✅ Sensor endpoint: OK")
        else:
            print(f"❌ Sensor endpoint failed: {response.status_code}")
    except:
        print("❌ Sensor endpoint: Server not responding")

    # Test latest endpoint
    try:
        response = requests.get("http://localhost:8000/latest")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Latest endpoint: OK - Weight: {data.get('weight')}g")
        else:
            print(f"❌ Latest endpoint failed: {response.status_code}")
    except:
        print("❌ Latest endpoint: Server not responding")


if __name__ == "__main__":
    print("IoT IV Bag Monitoring - Sensor Simulator")
    print("=" * 50)

    choice = input(
        "Choose option:\n1. Test API endpoints\n2. Run full simulation\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        test_api_endpoints()
    elif choice == "2":
        simulate_iv_bag_depletion()
    else:
        print("Invalid choice. Running test endpoints...")
        test_api_endpoints()
