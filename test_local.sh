#!/bin/bash
# Local testing script for QRL Trading Bot

set -e

echo "🚀 Starting local testing..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start Redis container
echo "🐳 Starting Redis container..."
if ! docker ps | grep -q qrl-redis; then
    docker run -d --name qrl-redis -p 6379:6379 redis:7-alpine
    sleep 2
fi

# Set environment variables
export PORT=8080
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Start Flask app in background
echo "🌐 Starting Flask application..."
python main.py &
APP_PID=$!
sleep 3

# Test endpoints
echo ""
echo "🧪 Testing endpoints..."
echo ""

echo "1️⃣ Testing root endpoint:"
curl -s http://localhost:8080/ | python3 -m json.tool
echo ""

echo "2️⃣ Testing health endpoint:"
curl -s http://localhost:8080/health | python3 -m json.tool
echo ""

echo "3️⃣ Testing status endpoint:"
curl -s http://localhost:8080/status | python3 -m json.tool
echo ""

echo "4️⃣ Starting bot:"
curl -s -X POST http://localhost:8080/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}' | python3 -m json.tool
echo ""

echo "5️⃣ Executing trading logic:"
curl -s -X POST http://localhost:8080/execute | python3 -m json.tool
echo ""

echo "6️⃣ Checking status after execution:"
curl -s http://localhost:8080/status | python3 -m json.tool
echo ""

# Cleanup
echo "🧹 Cleaning up..."
kill $APP_PID
docker stop qrl-redis
docker rm qrl-redis

echo ""
echo "✅ All tests passed!"
