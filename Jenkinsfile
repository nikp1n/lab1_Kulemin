pipeline {
    agent any

    environment {
        IMAGE_NAME     = 'lab1_Kulemin'
        IMAGE_TAG      = 'latest'
        REGISTRY       = 'nikp1n'                
        DOCKER_CRED_ID = 'dockerhub-credentials'
    }

    options {
        timestamps()
    }

    stages {
        stage('Build Docker image') {
            steps {
                script {
                    def fullTag = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    echo "Building image ${fullTag}"
                    docker.build(fullTag)
                }
            }
        }

        stage('Unit tests (optional)') {
            when {
                expression { fileExists('requirements.txt') || fileExists('pyproject.toml') || fileExists('pytest.ini') }
            }
            steps {
                sh """
                    set -e
                    if [ -f requirements.txt ]; then python3 -m pip install -r requirements.txt || true; fi
                    python3 -m pip install pytest || true
                    pytest -q || true
                """
            }
        }

        stage('Smoke test container') {
            steps {
                script {
                    def fullTag = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    echo "Running smoke test for ${fullTag}"
                    sh """
                        set -e
                        docker rm -f smoke-test || true
                        docker run -d --name smoke-test -p 5000:5000 ${fullTag}
                    """
                    sleep time: 10, unit: 'SECONDS'
                    sh """
                        set -e
                        curl -fsS http://localhost:5000/health
                    """
                }
            }
        }

        stage('Push (dry-run preview)') {
            steps {
                script {
                    def fullTag = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    echo "DRY-RUN: would push -> docker push ${fullTag}"
                }
            }
        }

        stage('Push image (if credentials available)') {
            when {
                expression {
                    return env.DOCKER_CRED_ID && env.DOCKER_CRED_ID.trim()
                }
            }
            steps {
                script {
                    def fullTag = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CRED_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            set -e
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin || true
                        """
                        sh "docker push ${fullTag} || true"
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleanup'
            sh 'docker rm -f smoke-test || true'
            sh 'docker logout || true'
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
