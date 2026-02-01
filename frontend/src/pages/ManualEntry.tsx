import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Upload, Download, Trash2, Edit, Check, X } from 'lucide-react';
import Card from '../components/Card';
import Loading from '../components/Loading';
import styles from './ManualEntry.module.css';
import api from '../services/api';

interface BankAccount {
  account_id: string;
  bank_name: string;
  account_type: string;
  current_balance_inr: number;
  is_primary: boolean;
}

interface Transaction {
  txn_id?: string;
  account_id: string;
  txn_timestamp: string;
  amount_inr: number;
  txn_type: 'credit' | 'debit';
  balance_after_txn: number;
  description: string;
  merchant_category: string;
}

const ManualEntry = () => {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'transaction' | 'account' | 'bulk'>('transaction');
  
  // Transaction form
  const [txnForm, setTxnForm] = useState<Transaction>({
    account_id: '',
    txn_timestamp: new Date().toISOString().split('T')[0],
    amount_inr: 0,
    txn_type: 'credit',
    balance_after_txn: 0,
    description: '',
    merchant_category: ''
  });

  // Account form
  const [accountForm, setAccountForm] = useState({
    account_number: '',
    bank_name: '',
    account_type: 'savings',
    is_primary: false
  });

  // Bulk import
  const [bulkData, setBulkData] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/transactions/bank-accounts');
      setAccounts(response.data);
      if (response.data.length > 0 && !txnForm.account_id) {
        setTxnForm(prev => ({ ...prev, account_id: response.data[0].account_id }));
      }
    } catch (error) {
      console.error('Failed to load accounts:', error);
      setErrorMessage('Failed to load bank accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/manual/transactions', txnForm);
      setSuccessMessage('Transaction added successfully!');
      setTxnForm({
        account_id: txnForm.account_id,
        txn_timestamp: new Date().toISOString().split('T')[0],
        amount_inr: 0,
        txn_type: 'credit',
        balance_after_txn: 0,
        description: '',
        merchant_category: ''
      });
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Failed to add transaction');
      setTimeout(() => setErrorMessage(''), 3000);
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/manual/bank-accounts', accountForm);
      setSuccessMessage('Bank account added successfully!');
      setAccountForm({
        account_number: '',
        bank_name: '',
        account_type: 'savings',
        is_primary: false
      });
      loadAccounts();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Failed to add account');
      setTimeout(() => setErrorMessage(''), 3000);
    }
  };

  const handleBulkImport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Parse CSV data
      const lines = bulkData.trim().split('\n');
      const headers = lines[0].split(',');
      
      const transactions = lines.slice(1).map(line => {
        const values = line.split(',');
        return {
          account_id: txnForm.account_id,
          txn_timestamp: values[0],
          txn_type: values[1] as 'credit' | 'debit',
          amount_inr: parseFloat(values[2]),
          description: values[3],
          merchant_category: values[4],
          balance_after_txn: parseFloat(values[5])
        };
      });

      await api.post('/manual/transactions/bulk', transactions);
      setSuccessMessage(`${transactions.length} transactions imported successfully!`);
      setBulkData('');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Failed to import transactions');
      setTimeout(() => setErrorMessage(''), 3000);
    }
  };

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      await api.post('/manual/analyze');
      setSuccessMessage('Data analyzed successfully! Check Insights page for results.');
      setTimeout(() => setSuccessMessage(''), 5000);
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Analysis failed');
      setTimeout(() => setErrorMessage(''), 3000);
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    const template = `date,type,amount,description,category,balance_after
2026-02-01,credit,50000,Freelance payment,freelancing,50000
2026-02-02,debit,500,Grocery shopping,groceries,49500
2026-02-03,credit,25000,Consulting fee,consulting,74500`;
    
    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transaction_template.csv';
    a.click();
  };

  if (loading && accounts.length === 0) {
    return <Loading />;
  }

  return (
    <div className={styles.manualEntry}>
      <div className={styles.header}>
        <div>
          <h1>Manual Data Entry</h1>
          <p>Add transactions, accounts, and income sources manually</p>
        </div>
        <button onClick={handleAnalyze} className={styles.analyzeBtn}>
          Analyze Data
        </button>
      </div>

      {successMessage && (
        <motion.div 
          className={styles.successMessage}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Check size={20} />
          {successMessage}
        </motion.div>
      )}

      {errorMessage && (
        <motion.div 
          className={styles.errorMessage}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <X size={20} />
          {errorMessage}
        </motion.div>
      )}

      <div className={styles.tabs}>
        <button 
          className={activeTab === 'transaction' ? styles.activeTab : ''}
          onClick={() => setActiveTab('transaction')}
        >
          <Plus size={18} />
          Add Transaction
        </button>
        <button 
          className={activeTab === 'account' ? styles.activeTab : ''}
          onClick={() => setActiveTab('account')}
        >
          <Plus size={18} />
          Add Account
        </button>
        <button 
          className={activeTab === 'bulk' ? styles.activeTab : ''}
          onClick={() => setActiveTab('bulk')}
        >
          <Upload size={18} />
          Bulk Import
        </button>
      </div>

      {activeTab === 'transaction' && (
        <Card title="Add Transaction" subtitle="Manually enter a transaction">
          <form onSubmit={handleCreateTransaction} className={styles.form}>
            <div className={styles.formGroup}>
              <label>Bank Account</label>
              <select
                value={txnForm.account_id}
                onChange={(e) => setTxnForm({ ...txnForm, account_id: e.target.value })}
                required
              >
                <option value="">Select account</option>
                {accounts.map(acc => (
                  <option key={acc.account_id} value={acc.account_id}>
                    {acc.bank_name} - {acc.account_type}
                  </option>
                ))}
              </select>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label>Date</label>
                <input
                  type="date"
                  value={txnForm.txn_timestamp}
                  onChange={(e) => setTxnForm({ ...txnForm, txn_timestamp: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label>Type</label>
                <select
                  value={txnForm.txn_type}
                  onChange={(e) => setTxnForm({ ...txnForm, txn_type: e.target.value as 'credit' | 'debit' })}
                  required
                >
                  <option value="credit">Income (Credit)</option>
                  <option value="debit">Expense (Debit)</option>
                </select>
              </div>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formGroup}>
                <label>Amount (₹)</label>
                <input
                  type="number"
                  value={txnForm.amount_inr}
                  onChange={(e) => setTxnForm({ ...txnForm, amount_inr: parseFloat(e.target.value) })}
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label>Balance After (₹)</label>
                <input
                  type="number"
                  value={txnForm.balance_after_txn}
                  onChange={(e) => setTxnForm({ ...txnForm, balance_after_txn: parseFloat(e.target.value) })}
                  min="0"
                  step="0.01"
                  required
                />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label>Description</label>
              <input
                type="text"
                value={txnForm.description}
                onChange={(e) => setTxnForm({ ...txnForm, description: e.target.value })}
                placeholder="e.g., Freelance payment from Client X"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label>Category</label>
              <input
                type="text"
                value={txnForm.merchant_category}
                onChange={(e) => setTxnForm({ ...txnForm, merchant_category: e.target.value })}
                placeholder="e.g., freelancing, groceries, rent"
                required
              />
            </div>

            <button type="submit" className={styles.submitBtn}>
              <Plus size={18} />
              Add Transaction
            </button>
          </form>
        </Card>
      )}

      {activeTab === 'account' && (
        <Card title="Add Bank Account" subtitle="Register a new bank account">
          <form onSubmit={handleCreateAccount} className={styles.form}>
            <div className={styles.formGroup}>
              <label>Bank Name</label>
              <input
                type="text"
                value={accountForm.bank_name}
                onChange={(e) => setAccountForm({ ...accountForm, bank_name: e.target.value })}
                placeholder="e.g., HDFC Bank, ICICI Bank"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label>Account Number</label>
              <input
                type="text"
                value={accountForm.account_number}
                onChange={(e) => setAccountForm({ ...accountForm, account_number: e.target.value })}
                placeholder="Enter account number"
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label>Account Type</label>
              <select
                value={accountForm.account_type}
                onChange={(e) => setAccountForm({ ...accountForm, account_type: e.target.value })}
                required
              >
                <option value="savings">Savings</option>
                <option value="current">Current</option>
                <option value="salary">Salary</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={accountForm.is_primary}
                  onChange={(e) => setAccountForm({ ...accountForm, is_primary: e.target.checked })}
                />
                Set as primary account
              </label>
            </div>

            <button type="submit" className={styles.submitBtn}>
              <Plus size={18} />
              Add Account
            </button>
          </form>
        </Card>
      )}

      {activeTab === 'bulk' && (
        <Card title="Bulk Import" subtitle="Import multiple transactions from CSV">
          <div className={styles.bulkImport}>
            <button onClick={downloadTemplate} className={styles.downloadBtn}>
              <Download size={18} />
              Download CSV Template
            </button>

            <form onSubmit={handleBulkImport} className={styles.form}>
              <div className={styles.formGroup}>
                <label>Select Account</label>
                <select
                  value={txnForm.account_id}
                  onChange={(e) => setTxnForm({ ...txnForm, account_id: e.target.value })}
                  required
                >
                  <option value="">Select account</option>
                  {accounts.map(acc => (
                    <option key={acc.account_id} value={acc.account_id}>
                      {acc.bank_name} - {acc.account_type}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.formGroup}>
                <label>Paste CSV Data</label>
                <textarea
                  value={bulkData}
                  onChange={(e) => setBulkData(e.target.value)}
                  placeholder="Paste CSV data here (including header row)"
                  rows={10}
                  required
                />
              </div>

              <button type="submit" className={styles.submitBtn}>
                <Upload size={18} />
                Import Transactions
              </button>
            </form>
          </div>
        </Card>
      )}

      <Card>
        <div className={styles.info}>
          <h3>💡 Tips for Manual Entry</h3>
          <ul>
            <li>Add bank accounts first before entering transactions</li>
            <li>Use consistent category names for better insights</li>
            <li>Mark income transactions as "credit" and expenses as "debit"</li>
            <li>Click "Analyze Data" after adding transactions to update predictions</li>
            <li>Use bulk import for adding multiple transactions at once</li>
          </ul>
        </div>
      </Card>
    </div>
  );
};

export default ManualEntry;
