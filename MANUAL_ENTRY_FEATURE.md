# 📝 Manual Data Entry Feature

## Overview

The Manual Entry feature allows users to add transactions, bank accounts, and income sources manually without connecting to banks. This is essential for:
- Users who want to start using the platform immediately
- Testing and demo purposes
- Users whose banks aren't supported yet
- Manual record keeping

---

## 🎯 Features

### 1. Manual Transaction Entry
- Add individual income or expense transactions
- Specify date, amount, type, category, and description
- Update account balance automatically
- Support for both credit (income) and debit (expense)

### 2. Bank Account Management
- Add multiple bank accounts
- Support for Savings, Current, and Salary accounts
- Set primary account
- Secure account number encryption

### 3. Bulk Import
- Import multiple transactions from CSV
- Download CSV template
- Batch processing for efficiency
- Validation and error handling

### 4. Data Analysis
- Trigger ML analysis on manually entered data
- Extract features automatically
- Update income sources
- Generate predictions and insights

---

## 📡 API Endpoints

### POST `/manual/transactions`
Create a single transaction manually.

**Request Body:**
```json
{
  "account_id": "uuid",
  "txn_timestamp": "2026-02-01T10:00:00",
  "amount_inr": 50000,
  "txn_type": "credit",
  "balance_after_txn": 50000,
  "description": "Freelance payment",
  "merchant_category": "freelancing"
}
```

**Response:**
```json
{
  "txn_id": "uuid",
  "user_id": "uuid",
  "account_id": "uuid",
  "txn_timestamp": "2026-02-01T10:00:00",
  "amount_inr": 50000,
  "txn_type": "credit",
  "balance_after_txn": 50000,
  "description": "Freelance payment",
  "merchant_category": "freelancing",
  "is_income": true,
  "created_at": "2026-02-01T10:00:00"
}
```

### POST `/manual/transactions/bulk`
Create multiple transactions at once.

**Request Body:**
```json
[
  {
    "account_id": "uuid",
    "txn_timestamp": "2026-02-01",
    "amount_inr": 50000,
    "txn_type": "credit",
    "balance_after_txn": 50000,
    "description": "Freelance payment",
    "merchant_category": "freelancing"
  },
  {
    "account_id": "uuid",
    "txn_timestamp": "2026-02-02",
    "amount_inr": 500,
    "txn_type": "debit",
    "balance_after_txn": 49500,
    "description": "Grocery shopping",
    "merchant_category": "groceries"
  }
]
```

**Response:**
```json
[
  { /* transaction 1 */ },
  { /* transaction 2 */ }
]
```

### POST `/manual/bank-accounts`
Add a bank account manually.

**Request Body:**
```json
{
  "account_number": "1234567890",
  "bank_name": "HDFC Bank",
  "account_type": "savings",
  "is_primary": true
}
```

**Response:**
```json
{
  "account_id": "uuid",
  "user_id": "uuid",
  "bank_name": "HDFC Bank",
  "account_type": "savings",
  "is_primary": true,
  "current_balance_inr": 0,
  "created_at": "2026-02-01T10:00:00"
}
```

### POST `/manual/income-sources`
Add an income source manually.

**Request Body:**
```json
{
  "source_name": "Freelancing",
  "source_category": "freelancing",
  "avg_monthly_inr": 50000
}
```

**Response:**
```json
{
  "source_id": "uuid",
  "user_id": "uuid",
  "source_name": "Freelancing",
  "source_category": "freelancing",
  "avg_monthly_inr": 50000,
  "contribution_pct": 100,
  "stability_score": 0.5,
  "last_payment_date": null
}
```

### POST `/manual/analyze`
Trigger ML analysis on manually entered data.

**Response:**
```json
{
  "status": "success",
  "message": "Data analyzed successfully",
  "insights_generated": 5,
  "predictions_generated": 3
}
```

### GET `/manual/template/csv`
Get CSV template for bulk import.

**Response:**
```json
{
  "template": "date,type,amount,description,category,balance_after\n...",
  "instructions": {
    "date": "Format: YYYY-MM-DD",
    "type": "credit (income) or debit (expense)",
    "amount": "Amount in INR (without commas)",
    "description": "Transaction description",
    "category": "Category (freelancing, groceries, food, etc.)",
    "balance_after": "Account balance after transaction"
  }
}
```

### DELETE `/manual/transactions/{transaction_id}`
Delete a manually entered transaction.

**Response:**
```json
{
  "status": "success",
  "message": "Transaction deleted"
}
```

### PUT `/manual/transactions/{transaction_id}`
Update a manually entered transaction.

**Request Body:** Same as POST `/manual/transactions`

**Response:** Updated transaction object

---

## 🎨 Frontend Components

### ManualEntry Page
**Location:** `frontend/src/pages/ManualEntry.tsx`

**Features:**
- Three tabs: Add Transaction, Add Account, Bulk Import
- Form validation
- Success/error messages
- CSV template download
- Data analysis trigger

**Tabs:**

#### 1. Add Transaction Tab
- Select bank account
- Enter date
- Choose type (Income/Expense)
- Enter amount
- Enter balance after transaction
- Add description
- Specify category

#### 2. Add Account Tab
- Enter bank name
- Enter account number (encrypted)
- Select account type (Savings/Current/Salary)
- Set as primary (checkbox)

#### 3. Bulk Import Tab
- Download CSV template button
- Select account for import
- Paste CSV data textarea
- Import button

---

## 📊 CSV Template Format

```csv
date,type,amount,description,category,balance_after
2026-02-01,credit,50000,Freelance payment,freelancing,50000
2026-02-02,debit,500,Grocery shopping,groceries,49500
2026-02-03,credit,25000,Consulting fee,consulting,74500
2026-02-04,debit,1200,Restaurant,food,73300
```

**Column Descriptions:**
- `date`: Transaction date (YYYY-MM-DD format)
- `type`: `credit` for income, `debit` for expense
- `amount`: Transaction amount in INR (no commas)
- `description`: Transaction description
- `category`: Category name (freelancing, groceries, etc.)
- `balance_after`: Account balance after this transaction

---

## 🔄 Workflow

### Adding Transactions Manually

1. **Add Bank Account First**
   - Navigate to Manual Entry page
   - Click "Add Account" tab
   - Fill in bank details
   - Submit

2. **Add Transactions**
   - Click "Add Transaction" tab
   - Select bank account
   - Fill in transaction details
   - Submit

3. **Analyze Data**
   - Click "Analyze Data" button
   - System extracts features
   - Updates income sources
   - Generates predictions
   - Creates insights

4. **View Results**
   - Check Dashboard for updated stats
   - View Income Breakdown for sources
   - Check Insights for recommendations
   - View predictions on Dashboard

### Bulk Import Workflow

1. **Download Template**
   - Click "Bulk Import" tab
   - Click "Download CSV Template"
   - Open in Excel/Google Sheets

2. **Fill Template**
   - Add your transactions
   - Follow format exactly
   - Save as CSV

3. **Import**
   - Select bank account
   - Copy CSV content
   - Paste in textarea
   - Click "Import Transactions"

4. **Analyze**
   - Click "Analyze Data"
   - Wait for processing
   - Check results

---

## 🔐 Security

### Account Number Encryption
- Account numbers are hashed using SHA-256
- Never stored in plain text
- One-way encryption (cannot be reversed)

### Authentication
- All endpoints require JWT authentication
- Users can only access their own data
- Token validation on every request

### Data Validation
- Pydantic schemas validate all inputs
- Type checking on frontend
- SQL injection prevention (ORM)
- XSS protection

---

## 💡 Usage Tips

### For Best Results:
1. **Add accounts first** before entering transactions
2. **Use consistent category names** for better insights
3. **Mark income as "credit"** and expenses as "debit"
4. **Click "Analyze Data"** after adding transactions
5. **Use bulk import** for adding multiple transactions

### Category Suggestions:
**Income:**
- freelancing
- consulting
- salary
- investment
- rental_income

**Expenses:**
- groceries
- rent
- utilities
- food
- transportation
- entertainment
- healthcare

---

## 🧪 Testing

### Test Manual Entry
```bash
# 1. Start servers
python -m uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev

# 2. Login
# Navigate to http://localhost:3001
# Login with testuser1@example.com / TestPass123

# 3. Add Account
# Go to Manual Entry > Add Account
# Fill in details and submit

# 4. Add Transaction
# Go to Add Transaction tab
# Fill in details and submit

# 5. Analyze
# Click "Analyze Data" button
# Check Dashboard for updates
```

### Test Bulk Import
```bash
# 1. Download template
# Click "Download CSV Template"

# 2. Fill template
# Add 5-10 transactions

# 3. Import
# Paste CSV data
# Click "Import Transactions"

# 4. Verify
# Check transactions in database
# Run analysis
```

---

## 📈 Future Enhancements

### Short Term
- [ ] Transaction editing UI
- [ ] Transaction deletion UI
- [ ] File upload for CSV (instead of paste)
- [ ] Transaction history view
- [ ] Export transactions to CSV

### Medium Term
- [ ] Recurring transaction templates
- [ ] Transaction categories autocomplete
- [ ] Duplicate detection
- [ ] Transaction search and filter
- [ ] Batch edit/delete

### Long Term
- [ ] Import from bank statements (PDF)
- [ ] OCR for receipt scanning
- [ ] Mobile app for quick entry
- [ ] Voice input for transactions
- [ ] Integration with accounting software

---

## 🐛 Troubleshooting

### Issue: "Account not found"
**Solution:** Add a bank account first before adding transactions

### Issue: "Failed to import transactions"
**Solution:** Check CSV format matches template exactly

### Issue: "Analysis failed"
**Solution:** Ensure you have at least 30 days of transaction data

### Issue: "No income sources showing"
**Solution:** Click "Analyze Data" to extract income sources from transactions

---

## 📚 Related Documentation

- `API_DOCUMENTATION.md` - Complete API reference
- `FRONTEND_COMPLETE.md` - Frontend architecture
- `ML_TRAINING_VALIDATION_REPORT.md` - ML model details
- `QUICK_REFERENCE.md` - Quick commands and tips

---

**Status:** ✅ Complete and Production-Ready  
**Version:** 1.0.0  
**Last Updated:** February 1, 2026
