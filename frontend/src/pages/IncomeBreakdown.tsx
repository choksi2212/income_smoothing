import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { TrendingUp, Activity } from 'lucide-react';
import { featuresAPI } from '../services/api';
import Card from '../components/Card';
import Loading from '../components/Loading';
import styles from './IncomeBreakdown.module.css';

const COLORS = ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#bdc3c7'];

const IncomeBreakdown = () => {
  const [incomeSources, setIncomeSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIncomeData();
  }, []);

  const loadIncomeData = async () => {
    try {
      setLoading(true);
      const sources = await featuresAPI.getIncomeSources();
      setIncomeSources(sources);
    } catch (error) {
      console.error('Failed to load income sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStabilityColor = (score: number) => {
    if (score >= 0.7) return 'var(--color-positive)';
    if (score >= 0.4) return 'var(--color-warning)';
    return 'var(--color-negative)';
  };

  const getStabilityLabel = (score: number) => {
    if (score >= 0.7) return 'High';
    if (score >= 0.4) return 'Medium';
    return 'Low';
  };

  if (loading) {
    return <Loading />;
  }

  if (incomeSources.length === 0) {
    return (
      <div className={styles.incomeBreakdown}>
        <div className={styles.header}>
          <div>
            <h1>Income Breakdown</h1>
            <p>Analyze your income sources and stability</p>
          </div>
        </div>
        <Card>
          <div className={styles.emptyState}>
            <Activity size={48} color="var(--text-secondary)" />
            <h3>No Income Sources Found</h3>
            <p>Add transactions to see your income breakdown, or go to Manual Entry to add data.</p>
          </div>
        </Card>
      </div>
    );
  }

  const chartData = incomeSources.map(source => ({
    name: source.source_name,
    value: parseFloat(source.contribution_pct),
  }));

  return (
    <div className={styles.incomeBreakdown}>
      <div className={styles.header}>
        <div>
          <h1>Income Breakdown</h1>
          <p>Analyze your income sources and stability</p>
        </div>
      </div>

      <div className={styles.grid}>
        <Card title="Income Distribution" subtitle="By source">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Income Sources" subtitle={`${incomeSources.length} active sources`}>
          <div className={styles.sourcesList}>
            {incomeSources.map((source, index) => (
              <motion.div
                key={source.source_id}
                className={styles.sourceCard}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className={styles.sourceHeader}>
                  <div className={styles.sourceName}>
                    <TrendingUp size={18} color={COLORS[index % COLORS.length]} />
                    <span>{source.source_name}</span>
                  </div>
                  <div className={styles.sourceContribution}>
                    {parseFloat(source.contribution_pct).toFixed(1)}%
                  </div>
                </div>

                <div className={styles.sourceDetails}>
                  <div className={styles.sourceDetail}>
                    <span>Avg Monthly:</span>
                    <span className={styles.amount}>{formatCurrency(parseFloat(source.avg_monthly_inr))}</span>
                  </div>
                  
                  <div className={styles.sourceDetail}>
                    <span>Stability:</span>
                    <span style={{ color: getStabilityColor(parseFloat(source.stability_score)), fontWeight: 600 }}>
                      {getStabilityLabel(parseFloat(source.stability_score))}
                    </span>
                  </div>

                  {source.last_payment_date && (
                    <div className={styles.sourceDetail}>
                      <span>Last Payment:</span>
                      <span>{new Date(source.last_payment_date).toLocaleDateString('en-IN')}</span>
                    </div>
                  )}
                </div>

                <div className={styles.stabilityBar}>
                  <div
                    className={styles.stabilityFill}
                    style={{
                      width: `${parseFloat(source.stability_score) * 100}%`,
                      backgroundColor: getStabilityColor(parseFloat(source.stability_score)),
                    }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <div className={styles.insights}>
          <Activity size={20} color="var(--color-warning)" />
          <div>
            <h3>Income Diversification Tips</h3>
            <ul>
              <li>Aim for at least 3-4 different income sources for better stability</li>
              <li>No single source should contribute more than 60% of total income</li>
              <li>Focus on building stable, recurring income streams</li>
              <li>Monitor payment patterns to predict cash flow better</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default IncomeBreakdown;
