import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, X, AlertCircle, TrendingUp, Activity } from 'lucide-react';
import { insightsAPI } from '../services/api';
import Loading from '../components/Loading';
import styles from './Insights.module.css';

const Insights = () => {
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const data = await insightsAPI.getInsights();
      setInsights(data);
    } catch (error) {
      console.error('Failed to load insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (insightId: string) => {
    try {
      await insightsAPI.markAsRead(insightId);
      setInsights(insights.map(i => 
        i.insight_id === insightId ? { ...i, is_read: true } : i
      ));
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const handleDismiss = async (insightId: string) => {
    try {
      await insightsAPI.dismiss(insightId);
      setInsights(insights.filter(i => i.insight_id !== insightId));
    } catch (error) {
      console.error('Failed to dismiss:', error);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'VOLATILITY_SPIKE':
      case 'EXPENSE_CREEP':
        return <AlertCircle size={20} />;
      case 'POSITIVE_TREND':
        return <TrendingUp size={20} />;
      default:
        return <Activity size={20} />;
    }
  };

  const formatInsightType = (type: string) => {
    return type.toLowerCase().replace(/_/g, ' ');
  };

  const formatMetricValue = (key: string, value: any) => {
    if (typeof value === 'number') {
      if (key.includes('pct') || key.includes('percent')) {
        return `${value.toFixed(1)}%`;
      }
      if (key.includes('inr') || key.includes('income') || key.includes('expense') || key.includes('avg')) {
        return new Intl.NumberFormat('en-IN', {
          style: 'currency',
          currency: 'INR',
          maximumFractionDigits: 0,
        }).format(value);
      }
      return value.toFixed(2);
    }
    return value;
  };

  if (loading) {
    return <Loading />;
  }

  if (insights.length === 0) {
    return (
      <div className={styles.insights}>
        <div className={styles.header}>
          <h1>Insights</h1>
          <p>AI-powered recommendations for your finances</p>
        </div>
        <div className={styles.emptyState}>
          <Activity size={48} color="var(--text-secondary)" />
          <h3>No insights yet</h3>
          <p>We'll analyze your transactions and provide personalized insights soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.insights}>
      <div className={styles.header}>
        <h1>Insights</h1>
        <p>AI-powered recommendations for your finances</p>
      </div>

      <div className={styles.insightsList}>
        {insights.map((insight, index) => (
          <motion.div
            key={insight.insight_id}
            className={`${styles.insightCard} ${!insight.is_read ? styles.unread : ''}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <div className={styles.insightHeader}>
              <div className={styles.insightTitle}>
                <div className={`${styles.severityBadge} ${styles[insight.severity]}`}>
                  {insight.severity}
                </div>
                {getInsightIcon(insight.insight_type)}
                <span className={styles.insightType}>
                  {formatInsightType(insight.insight_type)}
                </span>
              </div>
              <div className={styles.insightActions}>
                {!insight.is_read && (
                  <button
                    onClick={() => handleMarkAsRead(insight.insight_id)}
                    className={styles.actionBtn}
                    title="Mark as read"
                  >
                    <Eye size={18} />
                  </button>
                )}
                <button
                  onClick={() => handleDismiss(insight.insight_id)}
                  className={styles.actionBtn}
                  title="Dismiss"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <p className={styles.insightText}>{insight.explanation_text}</p>

            {insight.supporting_metrics && Object.keys(insight.supporting_metrics).length > 0 && (
              <div className={styles.insightMetrics}>
                {Object.entries(insight.supporting_metrics).map(([key, value]) => (
                  <div key={key} className={styles.metric}>
                    <span className={styles.metricLabel}>
                      {key.replace(/_/g, ' ')}
                    </span>
                    <span className={styles.metricValue}>
                      {formatMetricValue(key, value)}
                    </span>
                  </div>
                ))}
              </div>
            )}

            <div className={styles.insightFooter}>
              <span className={styles.insightDate}>
                {new Date(insight.created_at).toLocaleDateString('en-IN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
              {insight.is_read && (
                <span className={styles.readStatus}>Read</span>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Insights;
