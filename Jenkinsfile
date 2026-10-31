
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        DOCKERHUB_REPO = 'harini2926/nexora-web'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Nexora source downloaded successfully'
            }
        }

        stage('Docker Login Check') {
    steps {
        withCredentials([string(credentialsId: 'nexora-docker-token', variable: 'DH_TOKEN')]) {
            powershell '''
                $token = $env:DH_TOKEN.Trim()

                $sha = [Security.Cryptography.SHA256]::Create()
                $bytes = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($token))
                $hash = [BitConverter]::ToString($bytes).Replace("-", "")

                Write-Host "Jenkins fingerprint: $hash"

                $token | docker login --username harini2926 --password-stdin

                if ($LASTEXITCODE -ne 0) {
                    throw "Docker login failed"
                }
            '''
        }
    }
}

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t "%DOCKERHUB_REPO%:%BUILD_NUMBER%" .'

                bat 'docker tag "%DOCKERHUB_REPO%:%BUILD_NUMBER%" "%DOCKERHUB_REPO%:latest"'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                bat 'docker push "%DOCKERHUB_REPO%:%BUILD_NUMBER%"'

                bat 'docker push "%DOCKERHUB_REPO%:latest"'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    Write-Host "Deploying Nexora..."

                    kubectl apply -f k8s/pvc.yaml
                    if ($LASTEXITCODE -ne 0) {
                        throw "PVC failed"
                    }

                    kubectl apply -f k8s/service.yaml
                    if ($LASTEXITCODE -ne 0) {
                        throw "Service failed"
                    }

                    $image = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"

                    $yaml = Get-Content "k8s/deployment.yaml" -Raw
                    $yaml = $yaml.Replace("__IMAGE__", $image)

                    $yaml | kubectl apply -f -

                    if ($LASTEXITCODE -ne 0) {
                        throw "Deployment failed"
                    }

                    kubectl rollout status deployment/nexora-web --timeout=180s

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes rollout failed"
                    }

                    Write-Host "NEXORA DEPLOYED SUCCESSFULLY!"
                '''
            }
        }

    }

    post {
        success {
            echo 'SUCCESS: Nexora CI/CD pipeline completed!'
        }

        failure {
            echo 'FAILED: Check Console Output'
        }

        always {
            echo 'Nexora pipeline execution finished'
        }
    }
}
