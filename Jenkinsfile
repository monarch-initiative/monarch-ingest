pipeline {
    agent { label 'monarch-agent-large' }
    environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        BUILD_TIMESTAMP = sh(script: "echo `date +%s`", returnStdout: true).trim()
        PATH = "/opt/poetry/bin:${env.PATH}"
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')        
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
    }
    stages {
        stage('setup') {
            steps {
                sh '''
                    echo "Current directory: $(pwd)"
                    # export PATH=$PATH:$HOME/.local/bin
                    echo "Path: $PATH"
                    
                    # echo $SHELL
                    python3 --version
                    pip --version
                    poetry --version
                  

                    # poetry config experimental.new-installer false
                    poetry install --with dev
                    poetry run which ingest

                '''
            }
        }
        stage('download') {
            steps {
                sh '''
                    mkdir data || true
                    gsutil -q -m cp -r gs://monarch-ingest-data-cache/* data/
                    ls -lasdf
                    ls -la data
                '''
            }
        }
        stage('transform') {
            steps {
                sh 'poetry run ingest transform --all --log --rdf'
                sh '''
                   sed -i.bak 's@\r@@g' output/transform_output/*.tsv
                   rm output/transform_output/*.bak
                '''
                sh '''
                   gunzip output/rdf/*.gz
                   sed -i.bak 's@\\r@@g' output/rdf/*.nt
                   rm output/rdf/*.bak
                   gzip output/rdf/*.nt
                '''
            }
        }
        stage('merge') {
            steps {
                sh 'poetry run ingest merge'
            }
        }
        stage('kgx-graph-summary') {
            steps {
                sh 'poetry run kgx graph-summary -i tsv -c "tar.gz" --node-facet-properties provided_by --edge-facet-properties provided_by output/monarch-kg.tar.gz -o output/merged_graph_stats.yaml'
            }
        }
        stage('jsonl-conversion'){
            steps {
                sh 'poetry run ingest jsonl'
            }
        }
        stage('kgx-transforms'){
            steps {
                sh './scripts/kgx_transforms.sh'
            }
        }
        stage('denormalize') {
            steps {
                sh 'poetry run ingest closure'
            }
        }
        stage('solr') {
            steps {
                sh 'poetry run ingest solr'
            }
        }
        stage('sqlite') {
            steps {
                sh 'poetry run ingest sqlite'
            }
        }
        stage('make exports') {
            steps {
                sh 'poetry run ingest export'
            }
        }
        stage('upload files') {
            steps {
                sh 'poetry run ingest release --kghub'
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
                    pip install -r monarch-file-server/scripts/requirements.txt
                    python3 monarch-file-server/scripts/directory_indexer.py --inject monarch-file-server/scripts/directory-index-template.html --directory data-public --prefix https://data.monarchinitiative.org -x
                '''
            }
        }
    }
    post {
        always {
            sh 'docker rm -f neo || true'
        //    sh 'docker rm my_solr || true'
        }
        // upload data and output on failure
        failure {
            sh 'gsutil cp -r . gs://monarch-archive/monarch-kg-failed/${RELEASE}-${BUILD_TIMESTAMP}'
        }
    }
}
