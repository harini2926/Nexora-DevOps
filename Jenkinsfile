
pipeline {

    agent any

    environment {
        IMAGE_REPO = 'harini2926/nexora-web'
        APP_IMAGE = "${IMAGE_REPO}:${BUILD_NUMBER}"
        TEST_IMAGE = "nexora-selenium-tests:${BUILD_NUMBER}"
    }

    stages {

        // 1. Checkout source code
        stage('Checkout') {
            steps {
                echo 'Downloading Nexora source code'
                checkout scm
            }
        }

        // 2. Build Docker image
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_REPO%:%BUILD_NUMBER% .'
            }
        }

        // 3. Selenium automated testing
        stage('Selenium Testing') {
            steps {
                script {

                    bat '''
                    if not exist test-results mkdir test-results

                    docker network create nexora-ci-net

                    docker run -d --name nexora-ci-app ^
                    --network nexora-ci-net ^
                    --network-alias nexora-app ^
                    %IMAGE_REPO%:%BUILD_NUMBER%

                    docker run -d --name nexora-ci-selenium ^
                    --network nexora-ci-net ^
                    --network-alias selenium ^
                    --shm-size=2g ^
                    selenium/standalone-chrome:latest

                    docker build -t %TEST_IMAGE% -f tests/Dockerfile tests

                    docker run --rm ^
                    --network nexora-ci-net ^
                    -e BASE_URL=http://nexora-app:5000 ^
                    -e SELENIUM_URL=http://selenium:4444/wd/hub ^
                    -v "%WORKSPACE%/test-results:/reports" ^
                    %TEST_IMAGE%
                    '''
                }
            }
        }

        // 4. Push Docker image
        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {

                    bat '''
                    echo %DH_TOKEN% | docker login -u %DH_USER% --password-stdin

                    docker push %IMAGE_REPO%:%BUILD_NUMBER%

                    docker tag %IMAGE_REPO%:%BUILD_NUMBER% %IMAGE_REPO%:latest

                    docker push %IMAGE_REPO%:latest

                    docker logout
                    '''
                }
            }
        }

        // 5. Deploy to Kubernetes
        stage('Kubernetes Deployment') {
            steps {

                withCredentials([
                    file(
                        credentialsId: 'kubeconfig-file',
                        variable: 'KUBECONFIG'
                    )
                ]) {

                    bat '''
                    kubectl --kubeconfig "%KUBECONFIG%" apply -f k8s/pvc.yaml

                    kubectl --kubeconfig "%KUBECONFIG%" apply -f k8s/service.yaml

                    kubectl --kubeconfig "%KUBECONFIG%" apply -f k8s/deployment.yaml

                    kubectl --kubeconfig "%KUBECONFIG%" set image deployment/nexora-web nexora-web=%IMAGE_REPO%:%BUILD_NUMBER%

                    kubectl --kubeconfig "%KUBECONFIG%" rollout status deployment/nexora-web --timeout=180s

                    kubectl --kubeconfig "%KUBECONFIG%" get pods

                    kubectl --kubeconfig "%KUBECONFIG%" get services
                    '''
                }
            }
        }
    }

    post {

        always {
            script {
                bat 'docker rm -f nexora-ci-app nexora-ci-selenium 2>NUL || exit /b 0'
                bat 'docker network rm nexora-ci-net 2>NUL || exit /b 0'
            }

            junit(
                testResults: 'test-results/results.xml',
                allowEmptyResults: true
            )
        }

        success {
            echo 'NEXORA PIPELINE SUCCESSFUL!'
            echo 'Application deployed to Kubernetes.'
        }

        failure {
            echo 'NEXORA PIPELINE FAILED!'
            echo 'Check Jenkins console output.'
        }
    }
}
