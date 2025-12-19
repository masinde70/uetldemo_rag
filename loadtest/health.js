/**
 * k6 Load Test - Health Endpoints
 *
 * Tests health check endpoints for availability and latency.
 *
 * Usage:
 *   k6 run loadtest/health.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const healthErrorRate = new Rate('health_error_rate');
const healthLatency = new Trend('health_latency');

export const options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '30s', target: 50 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% under 500ms
    health_error_rate: ['rate<0.01'],    // Less than 1% errors
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  // Test basic health
  const basicStart = Date.now();
  const basicRes = http.get(`${BASE_URL}/api/v1/health`);
  healthLatency.add(Date.now() - basicStart);

  const basicSuccess = check(basicRes, {
    'basic health status 200': (r) => r.status === 200,
    'basic health ok': (r) => {
      try {
        return JSON.parse(r.body).status === 'ok';
      } catch {
        return false;
      }
    },
  });

  healthErrorRate.add(!basicSuccess);

  sleep(0.5);

  // Test detailed health (slower due to service checks)
  const detailedStart = Date.now();
  const detailedRes = http.get(`${BASE_URL}/api/v1/health/detailed`);
  healthLatency.add(Date.now() - detailedStart);

  const detailedSuccess = check(detailedRes, {
    'detailed health status 200': (r) => r.status === 200,
    'detailed health has services': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.services && body.capabilities;
      } catch {
        return false;
      }
    },
  });

  healthErrorRate.add(!detailedSuccess);

  sleep(0.5);
}
