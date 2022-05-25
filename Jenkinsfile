pipeline {
    agent any
    environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        PATH = "/home/ubuntu/.poetry/bin:${env.PATH}"

    }
    stages {
        stage('setup') {
            steps {
                sh '''
                    pip --version
                    python3 --version
                    echo $PATH
                    whoami
                    poetry install
                    poetry run which ingest
                '''
            }
        }
        stage('download') {
            steps {
                sh '''
                    mkdir data || true
                    gsutil -m cp -r gs://monarch-ingest/data-cache/* data/
                    ls -la
                    ls -la data
                '''
            }
        }
        stage('transform') {
            steps {
                sh 'poetry run ingest transform --all --rdf'
            }
        }
        stage('merge') {
            steps {
                sh 'poetry run ingest merge'
            }
        }
        stage('neo-transform'){
            steps {
                sh '''
                    docker rm -f neo || True
                    docker run --name neo -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/admin neo4j:3.4.15
                    poetry run which kgx
                    ls -la
                    ls -la output/
                    poetry run kgx transform --transform-config neo4j-transform.yaml
                    docker cp neo:/data .
                    tar czf neo4j.tar.gz data
                    mv neo4j.tar.gz output/
                '''
            }
        }
        stage('upload kgx files') {
            steps {
                sh 'poetry run ingest release --update-latest'
            }
        }
    }
    post {
        always {
            sh 'docker rm -f neo || True'
        }
    }
}
