import axios, { AxiosError, AxiosInstance } from 'axios';

/**
 * API 客户端缓存管理
 */
interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number;
}

class ApiCache {
  private cache = new Map<string, CacheEntry>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5分钟默认缓存时间

  set(key: string, data: any, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.DEFAULT_TTL,
    });
  }

  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    // 检查是否过期
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clear(): void {
    this.cache.clear();
  }

  remove(key: string): void {
    this.cache.delete(key);
  }
}

/**
 * 全局 API 缓存实例
 */
const apiCache = new ApiCache();

/**
 * 创建 API 客户端
 */
const apiClient: AxiosInstance = axios.create({
  // 自动检测 API URL
  baseURL: (() => {
    const isDev = import.meta.env.DEV;
    if (isDev) {
      // 开发环境：使用代理或直接连接
      return 'http://localhost:8000/api';
    } else {
      // 生产环境：使用相对路径
      return '/api';
    }
  })(),
  timeout: 30000, // 增加超时时间至30秒，处理长时间扫描
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 请求拦截器 - 添加认证令牌和日志
 */
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证令牌 (如果有的话)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 日志记录
    console.debug(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器 - 处理响应和错误
 */
apiClient.interceptors.response.use(
  (response) => {
    console.debug(`[API Response] ${response.status} ${response.config.url}`);
    return response.data;
  },
  (error: AxiosError) => {
    // 详细的错误处理
    if (error.response) {
      // 服务器响应了错误状态码
      const status = error.response.status;
      const data = error.response.data as any;

      console.error(
        `[API Error] ${status} ${error.config?.url}`,
        data?.message || error.message
      );

      // 根据不同的状态码处理
      switch (status) {
        case 400:
          console.error('Bad Request:', data?.detail || data?.message);
          break;
        case 401:
          // 认证失败 - 清除 token
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          console.error('Forbidden: 没有权限访问此资源');
          break;
        case 404:
          console.error('Not Found: 请求的资源不存在');
          break;
        case 500:
          console.error('Server Error:', data?.message || '服务器内部错误');
          break;
        default:
          console.error(`HTTP ${status}:`, data?.message || error.message);
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('[Network Error] No response from server', error.message);
    } else {
      // 在设置请求时出现问题
      console.error('[Setup Error]', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * API 客户端 Hook 和工具
 */
export const apiUtils = {
  /**
   * 获取缓存数据或发送请求
   */
  async getCached<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = apiCache.get(key);
    if (cached) {
      console.debug(`[Cache Hit] ${key}`);
      return cached;
    }

    const data = await fetcher();
    apiCache.set(key, data, ttl);
    return data;
  },

  /**
   * 清除缓存
   */
  clearCache(key?: string): void {
    if (key) {
      apiCache.remove(key);
    } else {
      apiCache.clear();
    }
  },

  /**
   * 检查 API 健康状态
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(
        `${apiClient.defaults.baseURL}/health`,
        { timeout: 5000 }
      );
      return response.status === 200;
    } catch {
      return false;
    }
  },
};

export default apiClient;
