pipeline {
    agent { label 'monarch-agent-large' }
        environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        PATH = "/home/ubuntu/.poetry/bin:${env.PATH}"
    }
    stages {
        stage('setup') {
            steps {
                sh '''
                    echo "Current directory: $(pwd)"
                    python3 --version
                    pip --version
                    export PATH=$PATH:$HOME/.local/bin
                    echo "Path: $PATH"

                    which poetry
                    poetry install
                    poetry run which ingest
                '''
            }
        }
        stage('download') {
            steps {
                sh '''
                    mkdir data || true
                    gsutil -q -m cp -r gs://monarch-ingest-data-cache/* data/
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
        // stage('neo4j-v3-transform'){
        //     steps {
        //         sh '''
        //             docker rm -f neo || True
        //             docker run --name neo -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/admin neo4j:3.4.15
        //             poetry run which kgx
        //             ls -la
        //             ls -la output/
        //             poetry run kgx transform --stream --transform-config neo4j-transform.yaml > /dev/null
        //             sleep 30s
        //             mkdir neo4j-v3 || true
        //             docker cp neo:/data ./neo4j-v3/data
        //             cd neo4j-v3
        //             tar czf neo4j-v3.tar.gz data
        //             mv neo4j-v3.tar.gz ../output/
        //         '''
        //     }
        // }
        stage('neo4j-v4-transform'){
            steps {
                sh '''
                    docker rm -f neo || True
                    mkdir neo4j-v4-data
                    docker run -d --name neo -p7474:7474 -p7687:7687 -v neo4j-v4-data:/data --env NEO4J_AUTH=neo4j/admin neo4j:4.4
                    poetry run kgx transform --stream --transform-config neo4j-transform.yaml
                    docker stop neo
                    docker run -v output:/backup -v neo4j-v4-data:/data --entrypoint neo4j-admin neo4j:4.4 dump --to /backup/monarch-kg.neo4j.dump
                '''
            }
        }
        stage('upload files') {
            steps {
                sh 'poetry run ingest release --update-buckets'
            }
        }
        stage('index') {
            steps {
                sh '''
                    echo "Current directory: $(pwd)"
                    python3 --version
                    pip --version
                    export PATH=$HOME/.local/bin:$PATH
                    echo "Path: $PATH"

                    cd $HOME
                    mkdir data-public
                    gcsfuse --implicit-dirs data-public-monarchinitiative data-public

                    git clone https://github.com/monarch-initiative/monarch-file-server.git
                    cd monarch-file-server/scripts
                    pip install -r requirements.txt

                    #python3 -m venv venv
                    #source venv/bin/activate
                    python3 ./directory_indexer.py -v --inject ./directory-index-template.html --directory ../data-public --prefix https://data.monarchinitiative.org -x
                '''
            }
        }
    }
    post {
        always {
            sh 'docker rm -f neo || true'
        //    sh 'docker rm my_solr || true'
        }
    }
}
