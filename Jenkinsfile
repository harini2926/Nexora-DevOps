stages {

    stage('Checkout') {
        steps {
            checkout scm
            echo 'Nexora source code downloaded'
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
                    $env:DH_TOKEN | docker login --username $env:DH_USER --password-stdin
                    if ($LASTEXITCODE -ne 0) { throw "Docker login failed" }

                    $tag = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"
                    $latest = "$($env:DOCKERHUB_REPO):latest"

                    docker push $tag
                    if ($LASTEXITCODE -ne 0) { throw "Docker push failed" }

                    docker tag $tag $latest
                    if ($LASTEXITCODE -ne 0) { throw "Docker tag failed" }

                    docker push $latest
                    if ($LASTEXITCODE -ne 0) { throw "Latest push failed" }

                    docker logout
                '''
            }
        }
    }

    stage('Deploy to Kubernetes') {
        steps {
            powershell '''
                kubectl apply -f k8s/pvc.yaml
                if ($LASTEXITCODE -ne 0) { throw "PVC failed" }

                kubectl apply -f k8s/service.yaml
                if ($LASTEXITCODE -ne 0) { throw "Service failed" }

                $image = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"

                $yaml = Get-Content "k8s/deployment.yaml" -Raw
                $yaml = $yaml.Replace("__IMAGE__", $image)

                $yaml | kubectl apply -f -
                if ($LASTEXITCODE -ne 0) { throw "Deployment failed" }

                kubectl rollout status deployment/nexora-web --timeout=180s
                if ($LASTEXITCODE -ne 0) { throw "Rollout failed" }
            '''
        }
    }
}
