/**
 * Server-Side Caching Layer
 *
 * Simple TTL-based cache to reduce API calls to PagerDuty.
 * Caching strategy:
 * - Static data (services, teams): 5 minutes
 * - Incident lists: 30 seconds
 * - Aggregated metrics: 60 seconds
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export class DataCache {
  private cache = new Map<string, CacheEntry<any>>();
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor() {
    // Clean up expired entries every 60 seconds
    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, 60000);
  }

  /**
   * Get data from cache or fetch if not cached/expired
   */
  async getOrFetch<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl: number
  ): Promise<T> {
    const cached = this.cache.get(key);

    // Check if cached and not expired
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      console.log(`[Cache HIT] ${key}`);
      return cached.data as T;
    }

    // Cache miss or expired - fetch fresh data
    console.log(`[Cache MISS] ${key}`);
    const data = await fetcher();

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });

    return data;
  }

  /**
   * Manually set a cache entry
   */
  set<T>(key: string, data: T, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  /**
   * Get cached data without fetching
   */
  get<T>(key: string): T | null {
    const cached = this.cache.get(key);

    if (!cached) {
      return null;
    }

    // Check if expired
    if (Date.now() - cached.timestamp >= cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data as T;
  }

  /**
   * Invalidate a specific cache key
   */
  invalidate(key: string): void {
    this.cache.delete(key);
    console.log(`[Cache INVALIDATE] ${key}`);
  }

  /**
   * Invalidate all cache entries matching a pattern
   */
  invalidatePattern(pattern: RegExp): void {
    const keysToDelete: string[] = [];

    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        keysToDelete.push(key);
      }
    }

    keysToDelete.forEach((key) => {
      this.cache.delete(key);
      console.log(`[Cache INVALIDATE] ${key}`);
    });
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    console.log("[Cache CLEAR] All entries cleared");
  }

  /**
   * Remove expired cache entries
   */
  private cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp >= entry.ttl) {
        keysToDelete.push(key);
      }
    }

    keysToDelete.forEach((key) => {
      this.cache.delete(key);
    });

    if (keysToDelete.length > 0) {
      console.log(`[Cache CLEANUP] Removed ${keysToDelete.length} expired entries`);
    }
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    size: number;
    entries: Array<{ key: string; age: number }>;
  } {
    const now = Date.now();
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      age: now - entry.timestamp,
    }));

    return {
      size: this.cache.size,
      entries,
    };
  }

  /**
   * Clean up resources
   */
  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    this.cache.clear();
  }
}

// Singleton instance
export const cache = new DataCache();

// Common TTL values (in milliseconds)
export const TTL = {
  STATIC: 5 * 60 * 1000, // 5 minutes - services, teams
  INCIDENTS: 30 * 1000, // 30 seconds - incident lists
  METRICS: 60 * 1000, // 60 seconds - aggregated metrics
  REALTIME: 10 * 1000, // 10 seconds - real-time stats
} as const;
