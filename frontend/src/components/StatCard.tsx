import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: 'positive' | 'negative' | 'neutral';
  subtitle?: string;
}

const StatCard = ({ label, value, icon, trend, subtitle }: StatCardProps) => {
  return (
    <motion.div
      className={styles.statCard}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className={styles.header}>
        <span className={styles.label}>{label}</span>
        {icon && <div className={styles.icon}>{icon}</div>}
      </div>
      
      <div className={`${styles.value} ${trend ? styles[trend] : ''}`}>
        {value}
      </div>
      
      {subtitle && <div className={styles.subtitle}>{subtitle}</div>}
    </motion.div>
  );
};

export default StatCard;
