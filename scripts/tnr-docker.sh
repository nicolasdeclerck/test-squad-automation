#!/usr/bin/env bash
# tnr-docker.sh — Manage the ephemeral Docker environment for regression tests.
#
# Usage:
#   ./scripts/tnr-docker.sh up      # Build, start, migrate, seed test data
#   ./scripts/tnr-docker.sh down    # Tear down and remove volumes
#   ./scripts/tnr-docker.sh status  # Show running services
#
# The environment is accessible at http://localhost:8080

set -euo pipefail

PROJECT_NAME="blog-tnr"
COMPOSE_FILE="docker-compose.test.yml"
COMPOSE="docker compose -p $PROJECT_NAME -f $COMPOSE_FILE"

cd "$(dirname "$0")/.."

usage() {
    echo "Usage: $0 {up|down|status}"
    echo ""
    echo "  up      Build and start the ephemeral TNR environment"
    echo "  down    Tear down the environment and remove all data"
    echo "  status  Show running services"
    exit 1
}

wait_for_django() {
    echo "Waiting for Django to be ready..."
    local retries=30
    while [ $retries -gt 0 ]; do
        if $COMPOSE exec -T django python -c "import django; django.setup()" 2>/dev/null; then
            echo "Django is ready."
            return 0
        fi
        retries=$((retries - 1))
        sleep 2
    done
    echo "ERROR: Django did not become ready in time."
    $COMPOSE logs django
    exit 1
}

seed_test_data() {
    echo "Seeding test data..."
    $COMPOSE exec -T django python manage.py shell <<'PYTHON'
from django.contrib.auth import get_user_model

User = get_user_model()

# Test user 1
if not User.objects.filter(email="testuser@example.com").exists():
    user1 = User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="Testpass123!",
        first_name="Test",
        last_name="User",
    )
    print(f"Created user: {user1.username}")
else:
    print("User testuser already exists")

# Test user 2
if not User.objects.filter(email="testuser2@example.com").exists():
    user2 = User.objects.create_user(
        username="testuser2",
        email="testuser2@example.com",
        password="Testpass123!",
        first_name="Test2",
        last_name="User2",
    )
    print(f"Created user: {user2.username}")
else:
    print("User testuser2 already exists")
PYTHON
    echo "Test data seeded."
}

cmd_up() {
    echo "Building and starting TNR environment..."
    $COMPOSE up --build -d

    echo "Running migrations..."
    $COMPOSE exec -T django python manage.py migrate --noinput

    seed_test_data

    echo ""
    echo "============================================"
    echo "  TNR environment ready!"
    echo "  URL: http://localhost:8080"
    echo "============================================"
    echo ""
    echo "Run regression tests with:"
    echo "  BASE_URL=http://localhost:8080 API_URL=http://localhost:8080 /regression-tests"
    echo ""
    echo "Tear down when done:"
    echo "  ./scripts/tnr-docker.sh down"
}

cmd_down() {
    echo "Tearing down TNR environment..."
    $COMPOSE down -v --remove-orphans
    echo "TNR environment removed."
}

cmd_status() {
    $COMPOSE ps
}

case "${1:-}" in
    up)     cmd_up ;;
    down)   cmd_down ;;
    status) cmd_status ;;
    *)      usage ;;
esac
