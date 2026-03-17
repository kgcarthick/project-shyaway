# ─────────────────────────────────────────────────────────────────────────────
#  Makefile  —  ShyAway Dashboard  /  Minikube + Kubernetes shortcuts
# ─────────────────────────────────────────────────────────────────────────────

IMAGE  := shyaway-dashboard
TAG    := local
NS     := default

.PHONY: all deploy teardown status build open logs restart

## Full deploy (start minikube → build image → apply k8s)
all: deploy

deploy:
	@bash deploy-minikube.sh deploy

## Tear down everything and stop Minikube
teardown:
	@bash deploy-minikube.sh teardown

## Show pod / service / log status
status:
	@bash deploy-minikube.sh status

## Build image only (inside Minikube's Docker daemon)
build:
	eval $$(minikube docker-env) && docker build -t $(IMAGE):$(TAG) .

## Open the dashboard in the default browser
open:
	minikube service shyaway-dashboard-service

## Tail live logs
logs:
	kubectl logs -n $(NS) -l app=shyaway-dashboard -f --tail=50

## Force a rolling restart (picks up new image without changing manifests)
restart:
	kubectl rollout restart deployment/shyaway-dashboard -n $(NS)
	kubectl rollout status  deployment/shyaway-dashboard -n $(NS) --timeout=120s
