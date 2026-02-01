import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Wallet, TrendingUp, Calendar, AlertCircle } from 'lucide-react';
import { smoothingAPI } from '../services/api';
import Card from '../components/Card';
import StatCard from '../components/StatCard';
import Loading from '../components/Loading';
import styles from './IncomeSmoothing.module.css';

const IncomeSmoothing = () => {
  const [buffer, setBuffer] = useState<any>(null);
  const [releases, setReleases] = useState<any[]>([]);
  const [releaseCalc, setReleaseCalc] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSmoothingData();
  }, []);

  const loadSmoothingData = async () => {
    try {
      setLoading(true);
      const [bufferData, releasesData, calcData] = await Promise.all([
        smoothingAPI.getBuffer(),
        smoothingAPI.getWeeklyReleases(),
        smoothingAPI.calculateRelease(),
      ]);
      
      setBuffer(bufferData);
      setReleases(releasesData);
      setReleaseCalc(calcData);
    } catch (error) {
      console.error('Failed to load smoothing data:', error);
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

  const getBufferHealthColor = (score: number) => {
    if (score < 0.3) return 'var(--color-positive)';
    if (score < 0.7) return 'var(--color-warning)';
    return 'var(--color-negative)';
  };

  const getBufferHealthLabel = (score: number) => {
    if (score < 0.3) return 'Healthy';
    if (score < 0.7) return 'Moderate';
    return 'At Risk';
  };

  if (loading) {
    return <Loading />;
  }

  const bufferUtilization = buffer ? (buffer.buffer_balance_inr / buffer.max_buffer_capacity_inr) * 100 : 0;

  return (
    <div className={styles.smoothing}>
      <div className={styles.header}>
        <div>
          <h1>Income Smoothing</h1>
          <p>Manage your income buffer and weekly releases</p>
        </div>
      </div>

      <div className={styles.statsGrid}>
        <StatCard
          label="Buffer Balance"
          value={formatCurrency(buffer?.buffer_balance_inr || 0)}
          icon={<Wallet size={20} />}
          trend="positive"
          subtitle={`${bufferUtilization.toFixed(1)}% utilized`}
        />
        
        <StatCard
          label="Total Deposited"
          value={formatCurrency(buffer?.total_deposited_inr || 0)}
          icon={<TrendingUp size={20} />}
          trend="neutral"
          subtitle="Lifetime deposits"
        />
        
        <StatCard
          label="Total Released"
          value={formatCurrency(buffer?.total_released_inr || 0)}
          icon={<TrendingUp size={20} />}
          trend="neutral"
          subtitle="Lifetime releases"
        />
        
        <StatCard
          label="Buffer Health"
          value={getBufferHealthLabel(buffer?.buffer_risk_score || 0)}
          icon={<AlertCircle size={20} />}
          trend={buffer?.buffer_risk_score < 0.3 ? 'positive' : buffer?.buffer_risk_score < 0.7 ? 'neutral' : 'negative'}
          subtitle={`Risk score: ${((buffer?.buffer_risk_score || 0) * 100).toFixed(0)}%`}
        />
      </div>

      <div className={styles.grid}>
        <Card title="Recommended Weekly Release" subtitle="Based on your income pattern">
          <div className={styles.releaseCard}>
            <div className={styles.releaseAmount}>
              {formatCurrency(releaseCalc?.recommended_weekly_release_inr || 0)}
            </div>
            <div className={styles.releaseDetails}>
              <div className={styles.releaseDetail}>
                <span>Buffer Health:</span>
                <span style={{ color: getBufferHealthColor(releaseCalc?.buffer_risk_score || 0) }}>
                  {(releaseCalc?.buffer_health * 100 || 0).toFixed(0)}%
                </span>
              </div>
              <div className={styles.releaseDetail}>
                <span>Worst Case Income:</span>
                <span>{formatCurrency(releaseCalc?.worst_case_income || 0)}</span>
              </div>
              <div className={styles.releaseDetail}>
                <span>Avg Weekly Income:</span>
                <span>{formatCurrency(releaseCalc?.avg_weekly_income || 0)}</span>
              </div>
            </div>
            
            {releaseCalc?.explanation && (
              <div className={styles.explanation}>
                <AlertCircle size={16} color="var(--color-warning)" />
                <p>{releaseCalc.explanation}</p>
              </div>
            )}
          </div>
        </Card>

        <Card title="Buffer Capacity" subtitle="Current utilization">
          <div className={styles.capacityBar}>
            <div
              className={styles.capacityFill}
              style={{
                width: `${bufferUtilization}%`,
                backgroundColor: bufferUtilization > 80 ? 'var(--color-negative)' : bufferUtilization > 50 ? 'var(--color-warning)' : 'var(--color-positive)',
              }}
            />
          </div>
          <div className={styles.capacityLabels}>
            <span>₹0</span>
            <span>{formatCurrency(buffer?.max_buffer_capacity_inr || 0)}</span>
          </div>
          <div className={styles.capacityDetails}>
            <div className={styles.capacityDetail}>
              <span>Current Balance:</span>
              <span>{formatCurrency(buffer?.buffer_balance_inr || 0)}</span>
            </div>
            <div className={styles.capacityDetail}>
              <span>Min Threshold:</span>
              <span>{formatCurrency(buffer?.min_buffer_threshold_inr || 0)}</span>
            </div>
            <div className={styles.capacityDetail}>
              <span>Max Capacity:</span>
              <span>{formatCurrency(buffer?.max_buffer_capacity_inr || 0)}</span>
            </div>
          </div>
        </Card>
      </div>

      <Card title="Recent Releases" subtitle="Last 8 weeks">
        <div className={styles.releasesList}>
          {releases.slice(0, 8).map((release, index) => (
            <motion.div
              key={release.release_id}
              className={styles.releaseItem}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className={styles.releaseItemHeader}>
                <div className={styles.releaseItemDate}>
                  <Calendar size={16} />
                  <span>{new Date(release.week_start_date).toLocaleDateString('en-IN')}</span>
                </div>
                <div className={`${styles.releaseStatus} ${release.is_released ? styles.released : styles.pending}`}>
                  {release.is_released ? 'Released' : 'Pending'}
                </div>
              </div>
              <div className={styles.releaseItemDetails}>
                <div className={styles.releaseItemDetail}>
                  <span>Recommended:</span>
                  <span>{formatCurrency(release.recommended_weekly_release_inr)}</span>
                </div>
                {release.is_released && (
                  <div className={styles.releaseItemDetail}>
                    <span>Actual:</span>
                    <span>{formatCurrency(release.actual_release_inr)}</span>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default IncomeSmoothing;
