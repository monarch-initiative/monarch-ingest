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
                    poetry run ingest transform --all
                '''
            }
        }
        stage('merge') {
            agent { dockerfile true }
            steps {
                sh 'poetry run ingest merge'
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
