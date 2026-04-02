import concurrent.futures
import requests
import time

# 🔥 IMPORTANT: use your EC2 IP
BASE_URL = "http://13.211.112.66:8080"

# API key (admin works for testing)
HEADERS = {
    "X-API-Key": "admin-123"
}

def send_request(i):
    try:
        start = time.time()

        # call GET endpoint
        response = requests.get(
            f"{BASE_URL}/api/parcels/test-{i}",
            headers=HEADERS
        )

        elapsed = time.time() - start

        return {
            "id": i,
            "status": response.status_code,
            "time": round(elapsed, 3)
        }

    except Exception as e:
        return {
            "id": i,
            "status": "FAILED",
            "time": 0,
            "error": str(e)
        }


def main():
    print("Starting load test with 20 concurrent requests...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(send_request, range(20)))

    success = 0

    for r in results:
        print(f"Request {r['id']}: {r['status']} in {r['time']}s")
        if r["status"] == 200 or r["status"] == 404:
            success += 1

    print("\n---------------------------")
    print(f"Successful responses: {success}/20")

    if success == 20:
        print("✅ Load test PASSED")
    else:
        print("❌ Load test FAILED")


if __name__ == "__main__":
    main()
