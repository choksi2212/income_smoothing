#!/bin/bash

echo "========================================"
echo "Prisma Setup for Income Smoothing"
echo "========================================"
echo ""

echo "Step 1: Installing Prisma..."
npm install

echo ""
echo "Step 2: Setting up environment..."
if [ ! -f "prisma/.env" ]; then
    echo "Creating prisma/.env file..."
    cp prisma/.env.example prisma/.env
    echo ""
    echo "IMPORTANT: Edit prisma/.env with your PostgreSQL password!"
    echo "Current DATABASE_URL needs your password."
    read -p "Press enter to continue after editing..."
fi

echo ""
echo "Step 3: Pulling database schema..."
npx prisma db pull

echo ""
echo "Step 4: Generating Prisma Client..."
npx prisma generate

echo ""
echo "========================================"
echo "Prisma Setup Complete!"
echo "========================================"
echo ""
echo "You can now:"
echo "  - Run 'npm run prisma:studio' to browse your database"
echo "  - Use Prisma Client in your code"
echo ""
echo "See PRISMA_SETUP.md for usage examples."
echo ""
