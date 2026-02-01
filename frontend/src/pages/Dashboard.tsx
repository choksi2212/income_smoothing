import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, DollarSign, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { predictionsAPI, insightsAPI, transactionsAPI } from '../services/api';
import StatCard from '../components/StatCard';
import Card from '../components/Card';
import Loading from '../components/Loading';
import styles from './Dashboard.module.css';

const Dashboard = () => {
  const [safeToSpend, setSafeToSpend] = useState<any>(null);
  const [predictions, setPredictions] = useState<any[]>([]);
  const [stabilityScore, setStabilityScore] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [safeData, predData, scoreData] = await Promise.all([
        predictionsAPI.getSafeToSpend(),
        predictionsAPI.getPredictions(),
        insightsAPI.getStabilityScore(),
      ]);
      
      setSafeToSpend(safeData);
      setPredictions(predData);
      setStabilityScore(scoreData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      await transactionsAPI.sync();
      await predictionsAPI.generatePredictions();
      await loadDashboardData();
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'var(--color-positive)';
      case 'medium': return 'var(--color-warning)';
      case 'high': return 'var(--color-negative)';
      default: return 'var(--text-secondary)';
    }
  };

  if (loading) {
    return <Loading />;
  }

  const prediction7d = predictions.find(p => p.prediction_window_days === 7);

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <div>
          <h1>Dashboard</h1>
          <p>Your financial overview at a glance</p>
        </div>
        <button onClick={handleSync} disabled={syncing} className={styles.syncBtn}>
          {syncing ? 'Syncing...' : 'Sync Data'}
        </button>
      </div>

      <div className={styles.statsGrid}>
        <StatCard
          label="Daily Safe to Spend"
          value={formatCurrency(safeToSpend?.daily_safe_spend_inr || 0)}
          icon={<DollarSign size={20} />}
          trend="neutral"
          subtitle="Conservative estimate"
        />
        
        <StatCard
          label="Weekly Safe to Spend"
          value={formatCurrency(safeToSpend?.weekly_safe_spend_inr || 0)}
          icon={<TrendingUp size={20} />}
          trend="neutral"
          subtitle="Next 7 days"
        />
        
        <StatCard
          label="Buffer Balance"
          value={formatCurrency(safeToSpend?.buffer_balance_inr || 0)}
          icon={<DollarSign size={20} />}
          trend="positive"
          subtitle="Available reserve"
        />
        
        <StatCard
          label="Income Stability"
          value={`${((stabilityScore?.stability_score || 0) * 100).toFixed(0)}%`}
          icon={<TrendingUp size={20} />}
          trend={stabilityScore?.stability_score > 0.7 ? 'positive' : stabilityScore?.stability_score > 0.4 ? 'neutral' : 'negative'}
          subtitle={stabilityScore?.interpretation || 'Medium'}
        />
      </div>

      {prediction7d && (
        <Card title="7-Day Cash Flow Prediction" subtitle="Expected income and expenses">
          <div className={styles.predictionDetails}>
            <div className={styles.predictionRow}>
              <span>Expected Inflow:</span>
              <span className={styles.positive}>{formatCurrency(prediction7d.expected_inflow_inr)}</span>
            </div>
            <div className={styles.predictionRow}>
              <span>Expected Outflow:</span>
              <span className={styles.negative}>{formatCurrency(prediction7d.expected_outflow_inr)}</span>
            </div>
            <div className={styles.predictionRow}>
              <span>Net Cash Flow:</span>
              <span className={prediction7d.net_cashflow_inr >= 0 ? styles.positive : styles.negative}>
                {formatCurrency(prediction7d.net_cashflow_inr)}
              </span>
            </div>
            <div className={styles.predictionRow}>
              <span>Risk Level:</span>
              <span style={{ color: getRiskColor(prediction7d.risk_level), fontWeight: 600 }}>
                {prediction7d.risk_level.toUpperCase()}
              </span>
            </div>
            <div className={styles.predictionRow}>
              <span>Confidence:</span>
              <span>{(prediction7d.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </Card>
      )}

      <Card title="Cash Flow Trend" subtitle="Historical and predicted">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={predictions.map(p => ({
            days: `${p.prediction_window_days}d`,
            inflow: p.expected_inflow_inr,
            outflow: p.expected_outflow_inr,
          }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
            <XAxis dataKey="days" stroke="var(--text-secondary)" />
            <YAxis stroke="var(--text-secondary)" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.5rem',
              }}
              formatter={(value: number) => formatCurrency(value)}
            />
            <Line
              type="monotone"
              dataKey="inflow"
              stroke="var(--color-positive)"
              strokeWidth={2}
              dot={{ fill: 'var(--color-positive)' }}
              name="Expected Inflow"
            />
            <Line
              type="monotone"
              dataKey="outflow"
              stroke="var(--color-negative)"
              strokeWidth={2}
              dot={{ fill: 'var(--color-negative)' }}
              name="Expected Outflow"
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {safeToSpend?.explanation && (
        <Card>
          <div className={styles.explanation}>
            <AlertCircle size={20} color="var(--color-warning)" />
            <p>{safeToSpend.explanation}</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
