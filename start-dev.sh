#!/bin/bash

echo "========================================"
echo "Starting SeraNova AI Development Servers"
echo "========================================"
echo ""

echo "[1/2] Starting Flask Backend..."
cd backend
python server.py &
BACKEND_PID=$!
cd ..

sleep 3

echo "[2/2] Starting React Frontend..."
<<<<<<< HEAD
cd frontend
=======
cd frontend_1
>>>>>>> 9b714ecfe3f2dbb84015c29a62856b5d69863a63
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Both servers are starting..."
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

