
pipeline {
    agent any

    environment {
        DOCKERHUB_REPO = 'harini2926/nexora-web'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Nexora source code downloaded successfully'
            }
        }

        stage('Python Syntax Check') {
            steps {
                bat 'python -m compileall -q front2'
                echo 'Python syntax check completed'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build -t "%DOCKERHUB_REPO%:%BUILD_NUMBER%" .
                '''
            }
        }

        stage('Login and Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    powershell '''
                        $ErrorActionPreference = "Stop"

                        $env:DH_TOKEN | docker login `
                            --username $env:DH_USER `
                            --password-stdin

                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker login failed"
                        }

                        $tag = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"
                        $latest = "$($env:DOCKERHUB_REPO):latest"

                        docker tag $tag $latest
                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker tag failed"
                        }

                        docker push $tag
                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker push failed"
                        }

                        docker push $latest
                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker latest push failed"
                        }

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    # Create database storage
                    kubectl apply -f k8s/pvc.yaml
                    if ($LASTEXITCODE -ne 0) {
                        throw "PVC creation failed"
                    }

                    # Create NodePort service
                    kubectl apply -f k8s/service.yaml
                    if ($LASTEXITCODE -ne 0) {
                        throw "Service creation failed"
                    }

                    # Prepare current Docker image
                    $image = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"

                    # Update deployment image
                    $yaml = Get-Content "k8s/deployment.yaml" -Raw
                    $yaml = $yaml.Replace("__IMAGE__", $image)

                    $yaml | kubectl apply -f -
                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes deployment failed"
                    }

                    # Wait for deployment
                    kubectl rollout status deployment/nexora-web --timeout=180s

                    if ($LASTEXITCODE -ne 0) {
                        throw "Kubernetes rollout failed"
                    }

                    Write-Host "Nexora deployed successfully!"
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Nexora CI/CD Pipeline completed!'
            echo 'Docker Hub image pushed and Kubernetes deployment updated.'
        }

        failure {
            echo 'FAILED: Check Jenkins Console Output for errors.'
        }

        always {
            echo 'Nexora pipeline execution finished.'
        }
    }
}
