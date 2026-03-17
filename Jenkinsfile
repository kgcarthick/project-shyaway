pipeline {
    agent any

    environment {
        IMAGE_NAME   = "shyaway-dashboard"
        IMAGE_TAG    = "local"
        GHCR_IMAGE   = "ghcr.io/kgcarthick/project-shyaway"
        GITHUB_CREDS = credentials('github-token')   // Jenkins credential ID → username/password (PAT)
    }

    triggers {
        githubPush()   // fires on every push via GitHub webhook
    }

    options {
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {

        // ── 1. Source ────────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                echo "Checked out branch: ${env.GIT_BRANCH}  commit: ${env.GIT_COMMIT?.take(8)}"
            }
        }

        // ── 2. Lint / Validate ───────────────────────────────────────────────
        stage('Validate') {
            steps {
                powershell '''
                    Write-Host "=== Python syntax check ==="
                    python -m py_compile visitor_dashboard.py
                    if ($LASTEXITCODE -ne 0) { throw "Syntax error in visitor_dashboard.py" }

                    Write-Host "=== Dockerfile lint (hadolint) ==="
                    if (Get-Command hadolint -ErrorAction SilentlyContinue) {
                        hadolint Dockerfile
                    } else {
                        Write-Warning "hadolint not found – skipping Dockerfile lint"
                    }
                    Write-Host "Validation passed."
                '''
            }
        }

        // ── 3. Build ─────────────────────────────────────────────────────────
        stage('Build Docker Image') {
            steps {
                powershell '''
                    Write-Host "=== Pointing Docker CLI at minikube daemon ==="
                    & minikube -p minikube docker-env --shell powershell | Invoke-Expression

                    Write-Host "=== Building image ==="
                    docker build -t "${env:IMAGE_NAME}:${env:IMAGE_TAG}" .
                    if ($LASTEXITCODE -ne 0) { throw "docker build failed" }

                    docker images "${env:IMAGE_NAME}:${env:IMAGE_TAG}"
                    Write-Host "Build complete."
                '''
            }
        }

        // ── 4. Push to GHCR ──────────────────────────────────────────────────
        stage('Push to GHCR') {
            steps {
                powershell '''
                    $commitShort = $env:GIT_COMMIT.Substring(0,8)

                    Write-Host "=== Logging in to ghcr.io ==="
                    $env:GITHUB_CREDS_PSW | docker login ghcr.io `
                        -u $env:GITHUB_CREDS_USR --password-stdin
                    if ($LASTEXITCODE -ne 0) { throw "docker login failed" }

                    Write-Host "=== Tagging ==="
                    docker tag "${env:IMAGE_NAME}:${env:IMAGE_TAG}" "${env:GHCR_IMAGE}:latest"
                    docker tag "${env:IMAGE_NAME}:${env:IMAGE_TAG}" "${env:GHCR_IMAGE}:${commitShort}"

                    Write-Host "=== Pushing ==="
                    docker push "${env:GHCR_IMAGE}:latest"
                    docker push "${env:GHCR_IMAGE}:${commitShort}"
                    Write-Host "Push complete."
                '''
            }
        }

        // ── 5. Deploy ─────────────────────────────────────────────────────────
        stage('Deploy to Kubernetes') {
            steps {
                powershell '''
                    Write-Host "=== Applying manifests ==="
                    kubectl apply -f k8s/deployment-local.yaml
                    kubectl apply -f k8s/service-nodeport.yaml

                    Write-Host "=== Rolling restart ==="
                    kubectl rollout restart deployment/$env:IMAGE_NAME
                    kubectl rollout status  deployment/$env:IMAGE_NAME --timeout=120s
                    if ($LASTEXITCODE -ne 0) { throw "Rollout did not complete in time" }
                    Write-Host "Deployment successful."
                '''
            }
        }

        // ── 6. Health Check ───────────────────────────────────────────────────
        stage('Health Check') {
            steps {
                powershell '''
                    Write-Host "=== Pod status ==="
                    kubectl get pods -l app=$env:IMAGE_NAME -o wide

                    Write-Host "=== Waiting for pods to be ready ==="
                    kubectl wait pod -l app=$env:IMAGE_NAME `
                        --for=condition=Ready --timeout=90s
                    if ($LASTEXITCODE -ne 0) { throw "Pods did not become Ready" }

                    $nodePort = kubectl get svc shyaway-dashboard-nodeport `
                        -o jsonpath="{.spec.ports[0].nodePort}" 2>$null
                    if ($nodePort) {
                        $nodeIp = minikube ip
                        Write-Host "Dashboard: http://${nodeIp}:${nodePort}"
                    }
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline PASSED — Shyaway dashboard is live."
        }
        failure {
            echo "Pipeline FAILED — review the stage logs above."
        }
        always {
            echo "Build #${env.BUILD_NUMBER} finished with status: ${currentBuild.currentResult}"
        }
    }
}
