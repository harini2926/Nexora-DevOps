
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
                echo 'Nexora source code downloaded successfully'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t "%DOCKERHUB_REPO%:%BUILD_NUMBER%" .'
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

                        $env:DH_TOKEN | docker login --username $env:DH_USER --password-stdin
                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker login failed"
                        }

                        $tag = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"
                        $latest = "$($env:DOCKERHUB_REPO):latest"

                        docker push $tag
                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker push failed"
                        }

                        docker tag $tag $latest
                        if ($LASTEXITCODE -ne 0) {
                            throw "Docker tag failed"
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

                    kubectl apply -f k8s/pvc.yaml
                    if ($LASTEXITCODE -ne 0) {
                        throw "PVC creation failed"
                    }

                    kubectl apply -f k8s/service.yaml
                    if ($LASTEXITCODE -ne 0) {
                        throw "Service creation failed"
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

                    Write-Host "Nexora deployed successfully!"
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Nexora CI/CD Pipeline completed!'
        }

        failure {
            echo 'FAILED: Check Console Output.'
        }

        always {
            echo 'Nexora pipeline execution finished.'
        }
    }
}
