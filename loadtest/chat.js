/**
 * k6 Load Test - Chat API
 *
 * Tests the chat endpoint under various load conditions.
 *
 * Usage:
 *   k6 run loadtest/chat.js
 *   k6 run --vus 10 --duration 30s loadtest/chat.js
 *
 * Environment variables:
 *   BASE_URL - API base URL (default: http://localhost:8000)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const chatErrorRate = new Rate('chat_error_rate');
const chatLatency = new Trend('chat_latency');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 5 },   // Ramp up to 5 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 20 },  // Spike to 20 users
    { duration: '1m', target: 10 },   // Back to 10
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],  // 95% of requests under 5s
    chat_error_rate: ['rate<0.1'],       // Less than 10% errors
    chat_latency: ['p(90)<4000'],        // 90th percentile under 4s
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Sample queries for different modes
const queries = [
  { message: "What is UETCL's strategic vision?", mode: 'strategy_qa' },
  { message: "What are the key strategic objectives?", mode: 'strategy_qa' },
  { message: "What actions reduce transmission losses?", mode: 'actions' },
  { message: "How can we improve grid reliability?", mode: 'actions' },
  { message: "Analyze the outage trends", mode: 'analytics' },
  { message: "What are ERA's grid code requirements?", mode: 'regulatory' },
];

export default function () {
  // Select a random query
  const query = queries[Math.floor(Math.random() * queries.length)];

  const payload = JSON.stringify({
    message: query.message,
    mode: query.mode,
    session_id: null,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-User-Email': `loadtest-${__VU}@test.com`,
    },
  };

  const startTime = Date.now();
  const response = http.post(`${BASE_URL}/api/v1/chat`, payload, params);
  const duration = Date.now() - startTime;

  // Record metrics
  chatLatency.add(duration);

  // Validate response
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'has answer': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.answer && body.answer.length > 0;
      } catch {
        return false;
      }
    },
    'has session_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.session_id && body.session_id.length > 0;
      } catch {
        return false;
      }
    },
  });

  chatErrorRate.add(!success);

  // Think time between requests
  sleep(Math.random() * 3 + 1);  // 1-4 seconds
}

export function handleSummary(data) {
  return {
    'loadtest/results/chat-summary.json': JSON.stringify(data, null, 2),
  };
}
