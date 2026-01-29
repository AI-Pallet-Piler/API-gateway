from datadog import DogStatsd

statsd = DogStatsd(host='datadog-agent', port=8125)

# Increment counter
statsd.increment('gateway.requests', tags=['endpoint:/users'])
