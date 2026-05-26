#!/bin/bash

# Data Engineering Interview Playground Setup Script
# This script automates the setup process for the interview playground

set -e

echo "🚀 Setting up Data Engineering Interview Playground"
echo "=========================================="

# Step 1: Environment setup
echo ""
echo "Step 1: Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python 3 found"

# Step 2: Create .env file
echo ""
echo "Step 2: Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
else
    echo "✅ .env file already exists"
fi

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 4: Start Docker containers
echo ""
echo "Step 4: Starting PostgreSQL with Docker..."
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Please install Docker and Docker Compose"
    echo "   Then run: docker-compose up -d"
else
    docker-compose up -d
    echo "✅ Docker containers started"
    
    # Wait for database to be ready
    echo "   Waiting for PostgreSQL to be ready..."
    sleep 5
fi

# Step 5: Seed database
echo ""
echo "Step 5: Seeding database with sample data..."
python seed_data.py
echo "✅ Database seeded"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "To start the Streamlit application:"
echo "  streamlit run playground.py"
echo ""
echo "To start the Jupyter notebook:"
echo "  jupyter notebook interview_notebook.ipynb"
echo ""
echo "Access the Streamlit app at: http://localhost:8501"
