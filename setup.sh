#!/bin/bash
set -e

echo "=== LeadGen AI Setup ==="

echo ""
echo "1. Setting up PostgreSQL database..."
psql -U postgres -c "CREATE DATABASE leadgen;" 2>/dev/null || echo "   (DB already exists, skipping)"

echo ""
echo "2. Setting up Python backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q
cp .env.example .env
echo "   -> Edit backend/.env and add your ANTHROPIC_API_KEY"

echo ""
echo "3. Setting up React frontend..."
cd ../frontend
npm install --silent

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env — add ANTHROPIC_API_KEY"
echo "  2. Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  3. Terminal 2: cd frontend && npm run dev"
echo "  4. Open: http://localhost:5173"
