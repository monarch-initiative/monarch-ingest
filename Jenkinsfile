pipeline {
    agent { label 'monarch-agent-xlarge' }
    environment {
        HOME = "${env.WORKSPACE}"
        RELEASE = sh(script: "echo `date +%Y-%m-%d`", returnStdout: true).trim()
        BUILD_TIMESTAMP = sh(script: "echo `date +%s`", returnStdout: true).trim()
        PATH = "/opt/uv:${env.PATH}"
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')        
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        GH_RELEASE_TOKEN = credentials('GH_RELEASE_TOKEN')
    }
    stages {
        stage('setup') {
            steps {
                sh '''
                    echo "Current directory: \\$(pwd)"
                    echo "Path: $PATH"

                    python3 --version
                    pip --version
                    uv --version

                    make install-full
                    uv run which ingest

                    # temporarily disabling, there isn't a .boto file
                    # create & edit ~/.boto to include AWS credentials
                    # sed -i "s@<your aws access key ID>@$(AWS_ACCESS_KEY_ID)@g" ~/.boto
                    # sed -i "s@<your aws secret access key>@$(AWS_SECRET_ACCESS_KEY)@g" ~/.boto
                '''
            }
        }
        stage('download') {
            steps {
                sh 'uv run ingest download --all'
                sh 'uv run ingest download-release-metadata'
            }
        }
        stage('transform') {
            steps {
                sh 'uv run ingest transform --all --log'
                sh '''
                   sed -i.bak 's@\r@@g' output/transform_output/*.tsv
                   rm output/transform_output/*.bak
                '''
            }
        }
        stage('merge') {
            steps {
                sh 'uv run ingest merge'
            }
        }
        stage('denormalize') {
            steps {
                sh 'uv run ingest closure'
            }
        }
        stage('report') {
            steps {
                sh 'uv run ingest report'
            }
        }
        stage('jsonl-conversion'){
            steps {
                sh 'uv run ingest jsonl'
            }
        }
        stage('neo4j-csv') {
            steps {
                sh 'uv run ingest neo4j-csv'
            }
        }
        // Materialize `_solr_edges` here so the parallel-processing stages
        // (including solr) can all open monarch-kg.duckdb read-only without
        // racing on a write lock.
        stage('prepare-solr') {
            steps {
                sh 'uv run ingest prepare-solr'
            }
        }
        stage('parallel-processing') {
            parallel {
                stage('kgx-graph-summary') {
                    steps {
                        sh 'uv run kgx graph-summary -i duckdb --node-facet-properties provided_by --edge-facet-properties provided_by output/monarch-kg.duckdb -o output/merged_graph_stats.yaml'
                    }
                }
                stage('connectivity-report') {
                    steps {
                        sh 'uv run ingest connectivity --input-db output/monarch-kg.duckdb --output output/connectivity_summary.yaml'
                    }
                }
                stage('solr') {
                    steps {
                        sh 'uv run ingest solr'
                    }
                }
                stage('kgx-transforms'){
                    steps {
                        sh '''
                            uv run kgx transform --stream --parallel 8 -i duckdb -f nt -o output/monarch-kg.nt output/monarch-kg.duckdb
                            pigz --force output/monarch-kg.nt
                        '''
                    }
                }
                stage('neo4j-dump') {
                    steps {
                        sh './scripts/load_neo4j.sh'
                    }
                }
                stage('sqlite') {
                    steps {
                        sh 'uv run ingest sqlite'
                    }
                }
                stage('make exports') {
                    steps {
                        sh 'uv run ingest export'
                    }
                }
            }
        }

        stage('build receipt') {
            steps {
                sh 'uv run ingest build-receipt --kg-version ${RELEASE}'
            }
        }
        stage('upload files') {
            steps {
                sh 'uv run ingest release --kghub'
            }
        }
        stage('create github release') {
            steps {
                sh 'uv run python scripts/create_github_release.py --kg-version ${RELEASE}'
            }
        }
        // stage('update dev deployment') {
        //     steps {
        //         sh 'uv run python scripts/update-dev-solr.py'
        //     }
        // }
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
            //             sh 'gsutil cp -r . gs://monarch-archive/monarch-kg-failed/${RELEASE}-${BUILD_TIMESTAMP}'
            sh 'gsutil cp -r output/* gs://monarch-archive/monarch-kg-experiment/${RELEASE}-${BUILD_TIMESTAMP}'
        }
    }
}
