# Database Configuration Options

This project provides **two ways** to interact with the PostgreSQL database:

## Option 1: SQLAlchemy (Current/Default)

**What it is**: Python ORM used by the FastAPI backend

**Pros**:
- ✅ Already configured and working
- ✅ Native Python integration
- ✅ All backend code uses it
- ✅ No additional setup needed

**Cons**:
- ❌ Requires manual model definitions
- ❌ No visual database browser
- ❌ More complex query syntax
- ❌ Limited type safety

**Setup**: Already done! Just use the existing backend.

**Location**: `app/models.py`, `app/database.py`

---

## Option 2: Prisma (Alternative)

**What it is**: Modern database toolkit with auto-generated client

**Pros**:
- ✅ Easier to set up and use
- ✅ Visual database browser (Prisma Studio)
- ✅ Auto-generated TypeScript types
- ✅ Intuitive query API
- ✅ Built-in migrations
- ✅ Better developer experience

**Cons**:
- ❌ Requires Node.js
- ❌ Additional installation step
- ❌ Not used by current backend (optional tool)

**Setup**: Run `setup-prisma.bat` (Windows) or `setup-prisma.sh` (Linux/Mac)

**Location**: `prisma/schema.prisma`

---

## Quick Comparison

| Feature | SQLAlchemy | Prisma |
|---------|-----------|--------|
| **Language** | Python | JavaScript/TypeScript |
| **Setup Time** | Already done | 5 minutes |
| **Visual Browser** | ❌ No | ✅ Yes (Prisma Studio) |
| **Type Safety** | Limited | Full |
| **Query Syntax** | ORM-style | Promise-based |
| **Migrations** | Alembic | Built-in |
| **Used By** | FastAPI Backend | Optional tooling |
| **Learning Curve** | Medium | Easy |

---

## When to Use What?

### Use SQLAlchemy if:
- You're working on the Python FastAPI backend
- You don't want to install additional tools
- You're comfortable with Python ORMs
- You want to keep things as-is

### Use Prisma if:
- You want a visual database browser
- You're building Node.js/TypeScript services
- You want easier database management
- You want better tooling and DX

### Use Both if:
- You want the best of both worlds
- SQLAlchemy for backend, Prisma for admin/tooling
- They work together perfectly (same database)

---

## Setup Instructions

### SQLAlchemy (Already Set Up)

```bash
# Just use the existing backend
python scripts/init_db.py
uvicorn app.main:app --reload
```

### Prisma (Optional Setup)

**Windows**:
```bash
setup-prisma.bat
```

**Linux/Mac**:
```bash
chmod +x setup-prisma.sh
./setup-prisma.sh
```

**Manual**:
```bash
# Install dependencies
npm install

# Configure database URL
cd prisma
copy .env.example .env
# Edit .env with your PostgreSQL credentials

# Pull schema from existing database
npx prisma db pull

# Generate Prisma Client
npx prisma generate

# Open database browser
npx prisma studio
```

---

## Example Usage

### SQLAlchemy (Python)

```python
from app.database import get_db
from app.models import User, Transaction

# Get user
db = next(get_db())
user = db.query(User).filter(User.email == "test@example.com").first()

# Get transactions
transactions = db.query(Transaction)\
    .filter(Transaction.user_id == user.user_id)\
    .order_by(Transaction.txn_timestamp.desc())\
    .limit(10)\
    .all()
```

### Prisma (JavaScript/TypeScript)

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
  orderBy: { txn_timestamp: 'desc' },
  take: 10
})
```

---

## Prisma Studio (Visual Database Browser)

One of Prisma's best features is the visual database browser:

```bash
npm run prisma:studio
```

This opens `http://localhost:5555` where you can:
- Browse all tables visually
- Filter and search data
- Edit records directly
- View relationships
- Export data

**No coding required!**

---

## Important Notes

1. **Both systems are independent**: They don't interfere with each other
2. **Same database**: Both connect to the same PostgreSQL instance
3. **No data duplication**: They read/write the same tables
4. **Choose based on need**: Use SQLAlchemy for backend, Prisma for tooling
5. **Existing code unchanged**: Adding Prisma doesn't modify any Python code

---

## Recommendation

**For most users**: Stick with SQLAlchemy (already working)

**For better tooling**: Add Prisma for database browsing and management

**For new features**: Consider Prisma if building Node.js services

---

## Troubleshooting

### SQLAlchemy Issues

```bash
# Test database connection
python scripts/test_db_connection.py

# Reinitialize database
python scripts/init_db.py
```

### Prisma Issues

```bash
# Test connection
npx prisma db pull

# Regenerate client
npx prisma generate

# Reset and try again
rm -rf node_modules
npm install
```

---

## Resources

**SQLAlchemy**:
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)

**Prisma**:
- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Studio](https://www.prisma.io/studio)
- [Prisma with PostgreSQL](https://www.prisma.io/docs/concepts/database-connectors/postgresql)

---

## Summary

You have **two options** for database management:

1. **SQLAlchemy** - Already working, used by backend ✅
2. **Prisma** - Optional, better tooling, visual browser 🎨

Both are valid choices. The existing SQLAlchemy setup works perfectly. Prisma is an optional enhancement for better developer experience.

**No need to choose one over the other** - they can coexist peacefully! 🤝
