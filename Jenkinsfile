
stage('Build, Login and Push Docker Image') {
    steps {
        withCredentials([
            string(
                credentialsId: 'nexora-docker-token',
                variable: 'DH_TOKEN'
            )
        ]) {
            powershell '''
                $ErrorActionPreference = "Stop"

                Write-Host "STEP 1: Docker Hub Login"

                $env:DH_TOKEN | docker login `
                    --username harini2926 `
                    --password-stdin

                if ($LASTEXITCODE -ne 0) {
                    throw "Docker login failed"
                }

                Write-Host "STEP 2: Building Nexora Image"

                $tag = "$($env:DOCKERHUB_REPO):$($env:BUILD_NUMBER)"
                $latest = "$($env:DOCKERHUB_REPO):latest"

                docker build -t $tag .

                if ($LASTEXITCODE -ne 0) {
                    throw "Docker build failed"
                }

                Write-Host "STEP 3: Pushing Image"

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
                    throw "Latest image push failed"
                }

                Write-Host "NEXORA IMAGE PUSHED SUCCESSFULLY"

                docker logout
            '''
        }
    }
}
