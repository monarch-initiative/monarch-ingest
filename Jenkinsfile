pipeline {
    agent { label 'monarch-agent-medium' }
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
                    poetry install
                    poetry run which ingest
                '''
            }
        }
        stage('download') {
            steps {
                sh '''
                    mkdir data || true
                    gsutil -q -m cp -r gs://monarch-ingest/data-cache/* data/
                    ls -la
                    ls -la data
                '''
            }
        }
        stage('transform') {
            steps {
                sh 'poetry run ingest transform --all --rdf --log'
            }
        }
        stage('merge') {
            steps {
                sh 'poetry run ingest merge'
            }
        }
        stage('neo-3-4-transform'){
            steps {
                sh '''
                    docker rm -f neo || True
                    docker run --name neo -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/admin neo4j:3.4.15
                    poetry run which kgx
                    ls -la
                    ls -la output/
                    python3 -mvenv venv
                    ./venv/bin/pip install kgx==1.5.2
                    ./venv/bin/kgx transform --stream --transform-config neo4j-v3-transform.yaml
                    sleep 30s
                    mkdir neo4j-v3 || true
                    docker cp neo:/data ./neo4j-v3/data
                    cd neo4j-v3
                    tar czf neo4j-v3.tar.gz data
                    mv neo4j-v3.tar.gz ../output/
                '''
            }
        }
//         stage('neo-4-3-transform'){
//             steps {
//                 sh '''
//                     docker rm -f neo || True
//                     docker run --name neo -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/admin neo4j:4.3
//                     poetry run which kgx
//                     ls -la
//                     ls -la output/
//                     poetry run kgx transform --stream --transform-config neo4j-v4-transform.yaml
//                     sleep 30s
//                     mkdir neo4j-v4 || true
//                     docker cp neo:/data ./neo4j-v4/data
//                     cd neo4j-v4
//                     tar czf neo4j-v4.tar.gz data
//                     mv neo4j-v4.tar.gz ../output/
//                 '''
//             }
//         }
//         stage("generate closure kgx files") {
//             steps {
//                 sh 'poetry run ingest closure'
//             }
//         }
//         stage("load solr") {
//             steps {
//                 sh 'poetry run ingest solr'
//             }
//         }
        stage('upload files') {
            steps {
                sh 'poetry run ingest release --update-latest'
            }
        }
    }
    post {
        always {
            sh 'docker rm -f neo || true'
//            sh 'docker rm my_solr || true'
        }
    }
}
