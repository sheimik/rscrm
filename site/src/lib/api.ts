/**
 * API клиент для взаимодействия с бэкендом
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ApiError {
  detail: string;
  code?: string;
}

export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Восстанавливаем токен из localStorage
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Если ответ пустой (например, для DELETE)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return null as T;
    }

    return response.json();
  }

  // Auth
  async login(username: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await fetch(`${this.baseUrl}/api/v1/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.detail || 'Ошибка авторизации');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  logout() {
    this.setToken(null);
  }

  async getCurrentUser() {
    return this.request('/api/v1/users/me');
  }

  // Objects
  async getObjects(params?: {
    city_id?: string;
    district_id?: string;
    status?: string;
    search?: string;
    page?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          query.append(key, String(value));
        }
      });
    }
    const queryString = query.toString();
    return this.request(`/api/v1/objects${queryString ? '?' + queryString : ''}`);
  }

  async getObject(id: string) {
    return this.request(`/api/v1/objects/${id}`);
  }

  async createObject(data: any) {
    return this.request('/api/v1/objects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateObject(id: string, data: any) {
    return this.request(`/api/v1/objects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Customers
  async getCustomers(params?: {
    q?: string;
    object_id?: string;
    phone?: string;
    interests?: string;
    rating_min?: number;
    rating_max?: number;
    page?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          query.append(key, String(value));
        }
      });
    }
    const queryString = query.toString();
    return this.request(`/api/v1/customers${queryString ? '?' + queryString : ''}`);
  }

  async getCustomer(id: string) {
    return this.request(`/api/v1/customers/${id}`);
  }

  async createCustomer(data: any) {
    return this.request('/api/v1/customers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCustomer(id: string, data: any) {
    return this.request(`/api/v1/customers/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Visits
  async getVisits(params?: {
    object_id?: string;
    customer_id?: string;
    engineer_id?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
    limit?: number;
  }) {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          query.append(key, String(value));
        }
      });
    }
    const queryString = query.toString();
    return this.request(`/api/v1/visits${queryString ? '?' + queryString : ''}`);
  }

  async getVisit(id: string) {
    return this.request(`/api/v1/visits/${id}`);
  }

  async createVisit(data: any) {
    return this.request('/api/v1/visits', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateVisit(id: string, data: any) {
    return this.request(`/api/v1/visits/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async completeVisit(id: string, data: any) {
    return this.request(`/api/v1/visits/${id}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Analytics
  async getSummary(period?: string, city_id?: string) {
    const query = new URLSearchParams();
    if (period) query.append('period', period);
    if (city_id) query.append('city_id', city_id);
    const queryString = query.toString();
    return this.request(`/api/v1/analytics/summary${queryString ? '?' + queryString : ''}`);
  }

  async getObjectsByCity() {
    return this.request('/api/v1/analytics/objects/by-city');
  }

  // Dictionaries
  async getCities() {
    return this.request('/api/v1/dictionaries/cities');
  }

  async getDistricts(cityId?: string) {
    const query = cityId ? `?city_id=${cityId}` : '';
    return this.request(`/api/v1/dictionaries/districts${query}`);
  }
}

export const api = new ApiClient();

