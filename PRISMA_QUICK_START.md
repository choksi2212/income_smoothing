# Prisma Quick Start (2 Minutes)

## What is This?

Prisma is an **optional alternative** to SQLAlchemy that makes database management easier. You don't need it - SQLAlchemy works fine - but Prisma gives you:

- 🎨 Visual database browser
- ⚡ Easier setup
- 🔧 Better tooling

## Do I Need This?

**NO** - Your project works perfectly with SQLAlchemy.

**YES** - If you want easier database management or visual tools.

## Quick Setup (Windows)

```bash
# 1. Run setup script
setup-prisma.bat

# 2. Edit prisma/.env with your password
# DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/income_smoothing_db?schema=public"

# 3. Open database browser
npm run prisma:studio
```

## Quick Setup (Linux/Mac)

```bash
# 1. Make script executable
chmod +x setup-prisma.sh

# 2. Run setup
./setup-prisma.sh

# 3. Edit prisma/.env with your password
# DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/income_smoothing_db?schema=public"

# 4. Open database browser
npm run prisma:studio
```

## What You Get

### Prisma Studio (Database Browser)
```bash
npm run prisma:studio
```
Opens `http://localhost:5555` where you can:
- Browse all tables visually
- Search and filter data
- Edit records directly
- View relationships
- No SQL needed!

### Easy Queries (JavaScript/TypeScript)
```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Get user
const user = await prisma.user.findUnique({
  where: { email: 'test@example.com' }
})

// Get transactions
const transactions = await prisma.transaction.findMany({
  where: { user_id: user.user_id },
  orderBy: { txn_timestamp: 'desc' }
})
```

## Common Commands

```bash
# Open database browser
npm run prisma:studio

# Pull latest schema from database
npm run prisma:pull

# Generate Prisma Client
npm run prisma:generate

# Complete setup
npm run prisma:setup
```

## Important Notes

1. **Optional**: You don't have to use this
2. **Safe**: Doesn't change existing code
3. **Same Database**: Uses your existing PostgreSQL database
4. **No Conflicts**: Works alongside SQLAlchemy

## Need Help?

- Full guide: [PRISMA_SETUP.md](PRISMA_SETUP.md)
- Comparison: [DATABASE_OPTIONS.md](DATABASE_OPTIONS.md)
- Details: [PRISMA_INTEGRATION.md](PRISMA_INTEGRATION.md)

## TL;DR

**Want visual database browser?**
```bash
setup-prisma.bat
npm run prisma:studio
```

**Happy with SQLAlchemy?**
Do nothing! Everything works as-is.

---

That's it! 🎉
