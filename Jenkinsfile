pipeline {
    agent any
    environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
    }
    stages {
        stage('setup') {
            agent { dockerfile true }
            steps {
                sh 'poetry install'
                sh 'poetry run which ingest'
            }
        }
        stage('download') {
            agent { dockerfile true }
            steps {
                sh 'mkdir data || true'
                sh 'gsutil -m cp -r gs://monarch-ingest/data-cache/* data/'
                sh 'ls -la'
                sh 'ls -la data'
            }
        }
        stage('transform') {
            agent { dockerfile true }
            steps {
                sh '''
                    poetry run ingest transform --all --rdf
                '''
            }
        }
        stage('merge') {
            agent { dockerfile true }
            steps {
                sh 'poetry run ingest merge'
            }
        }
        stage('neo-transform'){
            agent any
            steps {
                sh '''
                    docker rm -f neo || True
                    docker run --name neo -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/admin neo4j:3.4.15
                    pip --version
                    python3 --version
                    pip install poetry
                    alias poetry="~/.local/bin/poetry"
                    poetry install
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
            agent { dockerfile true }
            steps {
                sh 'poetry run ingest release --update-latest'
            }
        }
    }
}
