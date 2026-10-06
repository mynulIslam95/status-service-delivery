# status-service-delivery

Internal status HTTP service for Northfield Office: health, Prometheus metrics, Compose, Grafana dashboard, GitHub Actions, a failure drill, rollback, and Kubernetes manifests.

The application is small on purpose. The work is how it is built, watched and recovered.

Building an image is not a production deploy. CI here runs tests, builds the image and checks `/health`. Publishing to a registry is a separate step you add when you have a registry.

## Layout

```
app/main.py                 /health /ready /metrics
app/Dockerfile              non-root user 10001
docker-compose.yml          app, Prometheus, Grafana
prometheus/prometheus.yml
grafana/                    datasource + Northfield dashboard
tests/test_health.py
scripts/break.sh            STATUS_FAIL=1, expect 503
scripts/recover.sh          health 200 again
scripts/rollback.sh         previous image tag, then compose back
k8s/status.yaml             Deployment, Service, ConfigMap, probes
.github/workflows/ci.yml
```

## Run locally

```bash
python -m unittest tests/test_health.py
docker compose up --build
curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/metrics
```

Prometheus: http://127.0.0.1:9090  
Grafana: http://127.0.0.1:3000 (admin / `lab`)  
Dashboard **Northfield status** shows `northfield_health` and request count.

## Failure drill

```bash
chmod +x scripts/*.sh
./scripts/break.sh     # /health 503, northfield_health 0
# logs: docker compose logs app
# Grafana: Health panel drops
./scripts/recover.sh   # /health 200
```

## Rollback

```bash
docker build -t northfield-status:1.0.0 ./app
./scripts/rollback.sh northfield-status:1.0.0
```

Checks `X-App-Version`, then starts Compose again.

## CI

On push and pull request: unittest, `docker build`, `docker compose up` app, curl `/health`. A failing test blocks the change. Registry publish is not in this workflow.

## Kubernetes

kind or minikube:

```bash
docker build -t northfield-status:1.0.0 ./app
kind load docker-image northfield-status:1.0.0   # if kind
kubectl apply -f k8s/status.yaml
kubectl rollout status deploy/northfield-status
kubectl logs deploy/northfield-status
kubectl delete pod -l app=northfield-status   # new pod should become Ready
```

Dummy values only in the ConfigMap. Do not commit credentials.

Helm is not in this repo. Use the plain manifests until they are familiar.

## Verification
- Another person can `docker compose up` and hit `/health`
- CI is red when `test_health.py` fails
- Break → 503 and metric 0 → recover → 200
- Rollback script has been run against tag `1.0.0`
- `kubectl rollout status` succeeds on a local cluster when you apply `k8s/status.yaml`
