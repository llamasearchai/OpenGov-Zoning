"""Performance tests for OpenGov Zoning API using Locust."""

try:
    from locust import HttpUser, task, between, events
except ImportError as e:
    raise ImportError(
        "Locust is required for performance testing. "
        "Please install it with: pip install locust\n"
        "Original error: " + str(e)
    )
import json
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZoningAPIUser(HttpUser):
    """Load testing user for Zoning API endpoints."""

    # Wait time between requests (1-5 seconds)
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_token: str | None = None
        self.user_id: str | None = None

    def on_start(self):
        """Initialize user session."""
        logger.info(f"User {self.user_id} starting load test")
        self.authenticate_user()

    def on_stop(self):
        """Clean up user session."""
        logger.info(f"User {self.user_id} stopping load test")

    def authenticate_user(self):
        """Authenticate user and get token."""
        # Mock authentication - in real tests, this would be actual login
        self.auth_token = "mock_jwt_token_for_performance_testing"
        self.user_id = f"perf_test_user_{abs(hash(self)) % 10000}"

    @task(30)  # 30% of requests
    def health_check(self):
        """Test health check endpoint."""
        with self.client.get(
            "/health",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="Health Check"
        ) as response:
            if response.status_code == 200:
                logger.debug("Health check successful")
            else:
                logger.error(f"Health check failed: {response.status_code}")

    @task(25)  # 25% of requests
    def get_items(self):
        """Test getting items list."""
        with self.client.get(
            "/api/items",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="Get Items"
        ) as response:
            if response.status_code == 200:
                logger.debug("Get items successful")
            else:
                logger.error(f"Get items failed: {response.status_code}")

    @task(20)  # 20% of requests
    def create_item(self):
        """Test creating items."""
        item_data = {
            "name": f"Performance Test Item {time.time()}",
            "description": f"Created during performance test by user {self.user_id}"
        }

        with self.client.post(
            "/api/items",
            json=item_data,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            },
            name="Create Item"
        ) as response:
            if response.status_code == 200:
                logger.debug("Create item successful")
            else:
                logger.error(f"Create item failed: {response.status_code}")

    @task(15)  # 15% of requests
    def get_single_item(self):
        """Test getting a single item."""
        # Use a fixed item ID for performance testing
        item_id = "perf_test_item_123"

        with self.client.get(
            f"/api/items/{item_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="Get Single Item"
        ) as response:
            if response.status_code in [200, 404]:  # 404 is acceptable for non-existent items
                logger.debug("Get single item successful")
            else:
                logger.error(f"Get single item failed: {response.status_code}")

    @task(10)  # 10% of requests
    def run_analysis(self):
        """Test AI analysis endpoint."""
        analysis_data = {
            "prompt": f"Performance test analysis request from user {self.user_id}",
            "model": "ollama"
        }

        with self.client.post(
            "/api/analysis",
            json=analysis_data,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            },
            name="Run Analysis"
        ) as response:
            if response.status_code == 200:
                logger.debug("Analysis request successful")
            else:
                logger.error(f"Analysis request failed: {response.status_code}")


class APIAdminUser(HttpUser):
    """Administrative user for testing admin endpoints."""

    wait_time = between(2, 8)  # Slower for admin operations

    def on_start(self):
        """Initialize admin session."""
        self.auth_token: str = "mock_admin_jwt_token"
        self.user_id: str = f"admin_perf_test_user_{abs(hash(self)) % 10000}"

    @task(40)  # 40% of admin requests
    def get_stats(self):
        """Test getting system statistics."""
        with self.client.get(
            "/api/stats",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="Get Stats"
        ) as response:
            if response.status_code == 200:
                logger.debug("Get stats successful")
            else:
                logger.error(f"Get stats failed: {response.status_code}")

    @task(30)  # 30% of admin requests
    def bulk_operations(self):
        """Test bulk operations."""
        # Create multiple items in sequence
        for i in range(3):
            item_data = {
                "name": f"Bulk Item {i} - {time.time()}",
                "description": f"Bulk created item {i}"
            }

            with self.client.post(
                "/api/items",
                json=item_data,
                headers={
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                },
                name="Bulk Create Item"
            ) as response:
                if response.status_code != 200:
                    logger.error(f"Bulk create item {i} failed: {response.status_code}")

    @task(30)  # 30% of admin requests
    def concurrent_analysis(self):
        """Test concurrent analysis requests."""
        analysis_data = {
            "prompt": f"Concurrent analysis test from admin user {self.user_id}",
            "model": "openai"
        }

        with self.client.post(
            "/api/analysis",
            json=analysis_data,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            },
            name="Concurrent Analysis"
        ) as response:
            if response.status_code == 200:
                logger.debug("Concurrent analysis successful")
            else:
                logger.error(f"Concurrent analysis failed: {response.status_code}")


class StressTestUser(HttpUser):
    """User for stress testing with high load."""

    wait_time = between(0.1, 0.5)  # Very fast requests

    def on_start(self):
        """Initialize stress test session."""
        self.auth_token: str = "mock_stress_test_token"
        self.user_id: str = f"stress_test_user_{abs(hash(self)) % 10000}"
        self.request_count: int = 0

    @task(100)  # 100% of stress test requests
    def stress_health_check(self):
        """Stress test health check endpoint."""
        self.request_count += 1

        with self.client.get(
            "/health",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            name="Stress Health Check"
        ) as response:
            if response.status_code != 200:
                logger.error(f"Stress test request {self.request_count} failed: {response.status_code}")


# Event handlers for performance monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Handle test start event."""
    logger.info("Performance test starting...")
    logger.info(f"Running on {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Handle test stop event."""
    logger.info("Performance test completed.")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Monitor individual request performance."""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    elif response_time > 5000:  # Log slow requests (>5s)
        logger.warning(f"Slow request: {name} took {response_time}ms")


@events.worker_report.add_listener
def on_worker_report(client_id, data):
    """Handle worker reports in distributed testing."""
    logger.info(f"Worker {client_id} reported: {data}")


# Custom load test scenarios
class LoadTestScenarios:
    """Custom load test scenarios."""

    @staticmethod
    def gradual_ramp_up(env):
        """Gradually ramp up users over time."""
        logger.info("Starting gradual ramp-up scenario")

        # Start with 10 users
        env.runner.start(10, spawn_rate=1)

        # Ramp up to 50 users over 2 minutes
        def ramp_up():
            if env.runner.user_count < 50:
                env.runner.start(50, spawn_rate=2)
            else:
                # Ramp up to 100 users over next 2 minutes
                env.runner.start(100, spawn_rate=5)

        # Schedule ramp-up
        env.runner.schedule_task(ramp_up, delay=120)

    @staticmethod
    def spike_test(env):
        """Spike test - sudden increase in load."""
        logger.info("Starting spike test scenario")

        # Start with 10 users
        env.runner.start(10, spawn_rate=10)

        # Spike to 200 users after 30 seconds
        def spike():
            env.runner.start(200, spawn_rate=50)

        env.runner.schedule_task(spike, delay=30)

        # Reduce back to 10 users after spike
        def reduce_load():
            env.runner.start(10, spawn_rate=10)

        env.runner.schedule_task(reduce_load, delay=90)

    @staticmethod
    def stress_test(env):
        """Stress test - maximum load."""
        logger.info("Starting stress test scenario")

        # Immediately start with high load
        env.runner.start(500, spawn_rate=100)


# Performance assertion helpers
class PerformanceAsserts:
    """Helper class for performance assertions."""

    @staticmethod
    def assert_response_time_under(percentile_95, max_time_ms):
        """Assert that 95th percentile response time is under threshold."""
        assert percentile_95 < max_time_ms, f"95th percentile response time {percentile_95}ms exceeds threshold {max_time_ms}ms"

    @staticmethod
    def assert_error_rate_under(error_rate, max_error_rate):
        """Assert that error rate is under threshold."""
        assert error_rate < max_error_rate, f"Error rate {error_rate}% exceeds threshold {max_error_rate}%"

    @staticmethod
    def assert_requests_per_second(rps, min_rps):
        """Assert minimum requests per second."""
        assert rps >= min_rps, f"Requests per second {rps} is below minimum {min_rps}"


# Custom client for advanced testing
class AdvancedTestClient:
    """Advanced test client with custom functionality."""

    def __init__(self, base_url: str):
        self.base_url: str = base_url.rstrip('/')

    def make_authenticated_request(self, method: str, endpoint: str, token: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request with performance tracking."""
        import requests
        import time

        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {token}"

        start_time = time.time()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=kwargs.get('timeout', 30),  # Add default timeout
                **kwargs
            )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Ensure response is not None before accessing attributes
            if response is None:
                return {
                    'status_code': 0,
                    'response_time': response_time,
                    'success': False,
                    'error': 'Response is None'
                }

            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code < 400
            }

        except requests.exceptions.Timeout:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                'status_code': 408,  # Request Timeout
                'response_time': response_time,
                'success': False,
                'error': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            return {
                'status_code': 503,  # Service Unavailable
                'response_time': response_time,
                'success': False,
                'error': 'Connection error'
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                'status_code': 0,
                'response_time': response_time,
                'success': False,
                'error': str(e)
            }


# Configuration for different test environments
class TestConfig:
    """Configuration for different test environments."""

    LOCAL = {
        'host': 'http://localhost:8000',
        'users': 50,
        'spawn_rate': 5,
        'duration': 300  # 5 minutes
    }

    STAGING = {
        'host': 'https://staging.opengovzoning.com',
        'users': 100,
        'spawn_rate': 10,
        'duration': 600  # 10 minutes
    }

    PRODUCTION = {
        'host': 'https://api.opengovzoning.com',
        'users': 500,
        'spawn_rate': 50,
        'duration': 1800  # 30 minutes
    }