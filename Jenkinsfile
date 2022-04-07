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
                sh '''
                pwd
                ls
                poetry install
                '''
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
                    poetry run prefect storage set-default d61aac64-4ae1-42af-a114-b13621c8d11b
                    poetry run python monarch_ingest/pipeline.py
                '''
            }
        }
        stage('upload kgx files') {
            agent { dockerfile true }
            steps {
                sh 'gsutil -m cp -r output/*.tsv gs://monarch-ingest/${RELEASE}/output/'
            }
        }
    }
}
