#!/bin/bash

echo "🌱 CarbonSense - Quick Start Guide"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "web/index.html" ]; then
    echo "❌ Please run this script from the CarbonSense root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: web/index.html"
    exit 1
fi

echo "✅ Found CarbonSense project files"
echo ""

# Option 1: Open HTML file directly
echo "🚀 Option 1: Open Web Demo (Recommended)"
echo "----------------------------------------"
echo "Opening the static HTML demo in your default browser..."
echo ""

# For macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS - Opening with default browser..."
    open web/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux - Opening with default browser..."
    xdg-open web/index.html
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🪟 Detected Windows - Opening with default browser..."
    start web/index.html
else
    echo "❓ Unknown OS. Please manually open: web/index.html"
fi

echo ""
echo "📋 Demo Instructions:"
echo "1. Click 'Get Started' to see authentication"
echo "2. Sign up with any email (demo mode)"
echo "3. Explore the dashboard features"
echo "4. Add carbon activities and see calculations"
echo "5. View AI recommendations and achievements"
echo ""

# Option 2: Check for Node.js
echo "🔧 Option 2: Next.js Development (Production Version)"
echo "----------------------------------------------------"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js found: $NODE_VERSION"
    echo ""
    echo "To run the production Next.js version:"
    echo "  cd web"
    echo "  npm install"
    echo "  npm run dev"
    echo "  # Then open http://localhost:3000"
    echo ""
else
    echo "❌ Node.js not found. Install from: https://nodejs.org/"
    echo "   The static HTML version above works without Node.js!"
    echo ""
fi

# Option 3: Backend API
echo "🗄️  Option 3: Backend API (Optional)"
echo "-----------------------------------"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
    echo ""
    echo "To run the backend API:"
    echo "  cd backend"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  uvicorn app.main:app --reload"
    echo "  # Then visit http://localhost:8000/docs"
    echo ""
else
    echo "❌ Python not found. The web demo works without the backend!"
    echo ""
fi

echo "🎯 What You Can Do Right Now:"
echo "=============================="
echo "✅ Web demo is opening in your browser"
echo "✅ Try the carbon tracking features"
echo "✅ See real emission calculations"
echo "✅ Explore AI recommendations"
echo "✅ Test the achievement system"
echo ""
echo "📖 For more details, see README.md"
echo ""
echo "🌍 Happy carbon tracking! 🌱"