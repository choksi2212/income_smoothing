import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  phone: string;
  is_active: boolean;
  created_at: string;
}

export interface SafeToSpend {
  daily_safe_spend_inr: number;
  weekly_safe_spend_inr: number;
  predicted_cash_exhaustion_date: string | null;
  buffer_balance_inr: number;
  worst_case_income_7d: number;
  fixed_expenses_weekly: number;
  volatility_multiplier: number;
  explanation: string;
}

export interface CashflowPrediction {
  prediction_id: string;
  prediction_window_days: number;
  expected_inflow_inr: number;
  expected_outflow_inr: number;
  net_cashflow_inr: number;
  lower_bound_inr: number;
  upper_bound_inr: number;
  risk_level: 'low' | 'medium' | 'high';
  model_used: string;
  confidence_score: number;
  created_at: string;
}

export interface IncomeSource {
  source_id: string;
  source_name: string;
  source_category: string;
  avg_monthly_inr: number;
  contribution_pct: number;
  stability_score: number;
  last_payment_date: string | null;
}

export interface AIInsight {
  insight_id: string;
  insight_type: string;
  severity: 'info' | 'warning' | 'critical';
  explanation_text: string;
  supporting_metrics: Record<string, any>;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string;
}

export interface SmoothingBuffer {
  buffer_id: string;
  buffer_balance_inr: number;
  total_deposited_inr: number;
  total_released_inr: number;
  buffer_risk_score: number;
  min_buffer_threshold_inr: number;
  max_buffer_capacity_inr: number;
  last_deposit_date: string | null;
  last_release_date: string | null;
  updated_at: string;
}

export interface WeeklyRelease {
  release_id: string;
  week_start_date: string;
  recommended_weekly_release_inr: number;
  actual_release_inr: number;
  buffer_balance_before_inr: number;
  buffer_balance_after_inr: number;
  is_released: boolean;
  released_at: string | null;
  created_at: string;
}

// Auth APIs
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  register: async (data: { email: string; password: string; full_name: string; phone?: string }) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Predictions APIs
export const predictionsAPI = {
  getSafeToSpend: async (): Promise<SafeToSpend> => {
    const response = await api.get('/predictions/safe-to-spend');
    return response.data;
  },
  
  getPredictions: async (): Promise<CashflowPrediction[]> => {
    const response = await api.get('/predictions/');
    return response.data;
  },
  
  generatePredictions: async () => {
    const response = await api.post('/predictions/generate');
    return response.data;
  },
};

// Features APIs
export const featuresAPI = {
  getIncomeSources: async (): Promise<IncomeSource[]> => {
    const response = await api.get('/features/income-sources');
    return response.data;
  },
};

// Insights APIs
export const insightsAPI = {
  getInsights: async (unreadOnly = false): Promise<AIInsight[]> => {
    const response = await api.get('/insights/', { params: { unread_only: unreadOnly } });
    return response.data;
  },
  
  getStabilityScore: async () => {
    const response = await api.get('/insights/stability-score');
    return response.data;
  },
  
  markAsRead: async (insightId: string) => {
    const response = await api.patch(`/insights/${insightId}/read`);
    return response.data;
  },
  
  dismiss: async (insightId: string) => {
    const response = await api.patch(`/insights/${insightId}/dismiss`);
    return response.data;
  },
};

// Smoothing APIs
export const smoothingAPI = {
  getBuffer: async (): Promise<SmoothingBuffer> => {
    const response = await api.get('/smoothing/buffer');
    return response.data;
  },
  
  getWeeklyReleases: async (): Promise<WeeklyRelease[]> => {
    const response = await api.get('/smoothing/weekly-releases');
    return response.data;
  },
  
  calculateRelease: async () => {
    const response = await api.post('/smoothing/calculate-release');
    return response.data;
  },
};

// Transactions APIs
export const transactionsAPI = {
  sync: async () => {
    const response = await api.post('/transactions/sync');
    return response.data;
  },
};

export default api;
