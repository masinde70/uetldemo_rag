# Load Testing with k6

This directory contains k6 load test scripts for SISUiQ.

## Prerequisites

Install k6:

```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

## Running Tests

### Basic Usage

```bash
# Run chat load test
k6 run loadtest/chat.js

# Run health load test
k6 run loadtest/health.js
```

### Custom Configuration

```bash
# Custom VUs and duration
k6 run --vus 10 --duration 1m loadtest/chat.js

# Custom base URL
k6 run -e BASE_URL=http://staging.example.com loadtest/chat.js

# With output to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 loadtest/chat.js
```

## Test Scenarios

### chat.js

Tests the main chat API endpoint:
- Ramps from 5 to 20 concurrent users
- Uses random queries across all modes
- Thresholds: 95th percentile < 5s, error rate < 10%

### health.js

Tests health check endpoints:
- Up to 50 concurrent users
- Tests both basic and detailed health
- Thresholds: 95th percentile < 500ms, error rate < 1%

## Results

Results are saved to `loadtest/results/`.

## CI/CD Integration

Add to GitHub Actions:

```yaml
load-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install k6
      run: |
        curl -s https://dl.k6.io/key.gpg | sudo apt-key add -
        echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update && sudo apt-get install k6

    - name: Run load tests
      run: k6 run loadtest/chat.js

    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: load-test-results
        path: loadtest/results/
```
