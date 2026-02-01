# Prisma Setup Guide (Alternative to SQLAlchemy)

This project includes **both SQLAlchemy and Prisma** configurations. You can use either one - they both connect to the same PostgreSQL database.

## Why Prisma?

- **Easier Setup**: No need to manually configure SQLAlchemy
- **Type Safety**: Auto-generated TypeScript types
- **Better DX**: Intuitive query API
- **Visual Studio**: Built-in database browser with Prisma Studio

## Quick Setup

### 1. Install Prisma (Node.js required)

```bash
# Navigate to project root
cd income_smoothing

# Install Prisma CLI and Client
npm install -D prisma
npm install @prisma/client
```

### 2. Configure Database Connection

```bash
# Copy the example env file
cd prisma
copy .env.example .env

# Edit .env with your PostgreSQL credentials
# DATABASE_URL="postgresql://postgres:your_password@localhost:5432/income_smoothing_db?schema=public"
```

### 3. Connect to Existing Database

Since SQLAlchemy already created your tables, just pull the schema:

```bash
# Generate Prisma Client from existing database
npx prisma db pull

# Generate the Prisma Client
npx prisma generate
```

### 4. (Optional) Use Prisma Studio

Browse and edit your database visually:

```bash
npx prisma studio
```

This opens a web interface at `http://localhost:5555`

## Using Prisma in Your Code

### JavaScript/TypeScript Example

```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Get all users
const users = await prisma.user.findMany()

// Get user with relations
const user = await prisma.user.findUnique({
  where: { email: 'test@example.com' },
  include: {
    transactions: true,
    income_sources: true,
    bank_accounts: true
  }
})

// Create a transaction
const transaction = await prisma.transaction.create({
  data: {
    user_id: userId,
    account_id: accountId,
    txn_timestamp: new Date(),
    amount_inr: 5000,
    txn_type: 'credit',
    balance_after_txn: 15000,
    description: 'Freelance payment',
    merchant_category: 'freelancing',
    is_income: true
  }
})

// Complex queries with filters
const recentTransactions = await prisma.transaction.findMany({
  where: {
    user_id: userId,
    txn_timestamp: {
      gte: new Date('2024-01-01')
    },
    is_income: true
  },
  orderBy: {
    txn_timestamp: 'desc'
  },
  take: 10
})
```

### Python Example (using Prisma Client Python)

```bash
pip install prisma
```

```python
from prisma import Prisma

async def main():
    prisma = Prisma()
    await prisma.connect()
    
    # Get all users
    users = await prisma.user.find_many()
    
    # Get user with relations
    user = await prisma.user.find_unique(
        where={'email': 'test@example.com'},
        include={
            'transactions': True,
            'income_sources': True,
            'bank_accounts': True
        }
    )
    
    await prisma.disconnect()
```

## Key Differences from SQLAlchemy

| Feature | SQLAlchemy | Prisma |
|---------|-----------|--------|
| Setup | Manual models + migrations | Auto-generated from schema |
| Queries | Session-based ORM | Promise-based client |
| Type Safety | Limited (Python) | Full (TypeScript) |
| Migrations | Alembic required | Built-in `prisma migrate` |
| Studio | No visual tool | Prisma Studio included |

## Common Commands

```bash
# Pull schema from existing database
npx prisma db pull

# Generate Prisma Client
npx prisma generate

# Open Prisma Studio (database browser)
npx prisma studio

# Create a migration (if making schema changes)
npx prisma migrate dev --name migration_name

# Push schema changes to database
npx prisma db push

# Reset database (careful!)
npx prisma migrate reset
```

## Important Notes

1. **Both systems work together**: SQLAlchemy (Python backend) and Prisma (optional) connect to the same database
2. **No conflicts**: They use the same table structure
3. **Choose one**: Use SQLAlchemy for Python FastAPI backend, or Prisma if building Node.js services
4. **Existing data safe**: Prisma won't modify your existing SQLAlchemy tables

## Troubleshooting

### Connection Issues

If you get connection errors:

```bash
# Test connection
npx prisma db pull
```

### Schema Mismatch

If schema doesn't match:

```bash
# Force pull from database
npx prisma db pull --force
npx prisma generate
```

### Port Already in Use (Prisma Studio)

```bash
# Use different port
npx prisma studio --port 5556
```

## When to Use What?

- **Use SQLAlchemy**: If you're working with the existing Python FastAPI backend
- **Use Prisma**: If you're building new Node.js/TypeScript services or want better tooling
- **Use Both**: They can coexist - use SQLAlchemy for backend, Prisma for admin tools

## Resources

- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Client API](https://www.prisma.io/docs/reference/api-reference/prisma-client-reference)
- [Prisma Studio](https://www.prisma.io/studio)
- [Prisma with PostgreSQL](https://www.prisma.io/docs/concepts/database-connectors/postgresql)
