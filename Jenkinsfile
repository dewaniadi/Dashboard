def app = 'Unknown'
pipeline {
    agent any
    stages {
        stage('build'){
            steps{
                script{
                    app = docker.build("dewaniadi/Dashboard")
                    docker.withRegistry('', 'docker-hub'){
                        app.push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }
    }  
}
