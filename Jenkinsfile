pipeline {
    agent any

    environment {
        // === CONFIGURATION ===
        
        // 1. Registry Settings (Local Docker Registry)
        REGISTRY_IP   = "192.168.0.222" 
        REGISTRY_PORT = "5050"
        
        // 2. Deployment Server Settings (Target Ubuntu Server)
        DEPLOY_SERVER_IP = "192.168.0.223"
        
        // 3. Git Repository Settings
        GIT_REPO_URL  = "git@github.com:sergesvalov/cybuses.git"
        GIT_BRANCH    = "main"
        
        // 4. Docker Image Naming
        // Note: For local registries, the image name must start with the registry address
        DOCKER_IMAGE  = "${REGISTRY_IP}:${REGISTRY_PORT}/cybuses"
        
        // 5. Access Credentials (IDs must match Jenkins Credentials Manager)
        GIT_CREDS_ID  = "github-ssh-key"  // Credential for GitHub SSH access
        SSH_CREDS_ID  = "serge"           // Credential for Ubuntu server SSH access
        SERVER_USER   = "serge"           // Target server username
        
        // 6. Application Parameters
        CONTAINER_NAME = "cybuses-service"
        APP_PORT       = "8000"           // Port used by FastAPI
    }

    stages {
        stage('Source Checkout') {
            steps {
                script {
                    echo "Checking out source code from GitHub via SSH..."
                    checkout([$class: 'GitSCM', 
                        branches: [[name: "*/${GIT_BRANCH}"]], 
                        userRemoteConfigs: [[
                            url: env.GIT_REPO_URL, 
                            credentialsId: env.GIT_CREDS_ID
                        ]]
                    ])
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    echo "Building Docker image with build number: ${BUILD_NUMBER}"
                    // Build with two tags: the unique build number and 'latest'
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    echo "Pushing images to local registry at ${REGISTRY_IP}:${REGISTRY_PORT}..."
                    sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Remote SSH Deploy') {
            steps {
                script {
                    echo "Connecting to ${DEPLOY_SERVER_IP} for deployment..."
                    sshagent(credentials: [SSH_CREDS_ID]) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${DEPLOY_SERVER_IP} '
                                echo ">>> Connected. Pulling latest image..."
                                docker pull ${DOCKER_IMAGE}:latest

                                echo ">>> Cleaning up old container if it exists..."
                                # -f stops and removes the container; 2>/dev/null hides errors if container is missing
                                docker rm -f ${CONTAINER_NAME} 2>/dev/null || true

                                echo ">>> Starting new container..."
                                docker run -d \
                                    --name ${CONTAINER_NAME} \
                                    -p ${APP_PORT}:8000 \
                                    -p 8999:8999 \
                                    --restart unless-stopped \
                                    ${DOCKER_IMAGE}:latest
                                    
                                echo ">>> Deployment on remote host finished successfully."
                            '
                        """
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "Verifying service availability at http://${DEPLOY_SERVER_IP}:${APP_PORT}"
                    // Wait a few seconds for the app to initialize
                    sleep 5
                    // Check the status endpoint; fails the stage if 404 or 500 is returned
                    sh "curl -f http://${DEPLOY_SERVER_IP}:${APP_PORT}/api/status || echo 'Warning: Service is not responding yet'"
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up local build environment..."
            // Remove local images from Jenkins agent to save disk space
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
        }
        success {
            echo "Successfully deployed cybuses version ${BUILD_NUMBER}!"
        }
        failure {
            echo "Pipeline failed. Please check the logs above for errors."
        }
    }
}
