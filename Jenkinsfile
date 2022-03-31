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
            agent { label 'worker'}
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
                    poetry run koza transform --source monarch_ingest/alliance/gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/alliance/gene_to_phenotype.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/alliance/publication.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/ctd/chemical_to_disease.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/flybase/publication_to_gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/goa/go_annotation.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/hgnc/gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/hpoa/disease_phenotype.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/mgi/publication_to_gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/omim/gene_to_disease.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/panther/ref_genome_orthologs.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/pombase/gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/pombase/gene_to_phenotype.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/reactome/chemical_to_pathway.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/reactome/gene_to_pathway.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/rgd/publication_to_gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/sgd/publication_to_gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/string/protein_links.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/xenbase/gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/xenbase/gene_to_phenotype.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/xenbase/publication_to_gene.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/zfin/gene_to_phenotype.yaml --row-limit 1000
                    poetry run koza transform --source monarch_ingest/zfin/publication_to_gene.yaml --row-limit 1000
                '''
            }
        }
        stage('upload kgx files') {
            agent { label 'worker'}
            steps {
                sh 'gsutil -m cp -r output/*.tsv gs://monarch-ingest/experimental-output/${RELEASE}/output/'
//                sh 'gsutil -m cp -r output/*.yaml gs://monarch-ingest/experimental-output/${RELEASE}/output/'
            }
        }
        stage('merge') {
            agent {
                dockerfile { label 'large-worker' }
            }
            steps {
                sh '''poetry install'''
                sh '''poetry run kgx merge --merge-config merge.yaml -p 8 '''
            }
        }
        stage('upload merged') {
            agent { label 'worker'}
            steps {
                sh '''
                    gsutil cp output/merged/monarch-kg.tar.gz gs://monarch-ingest/experimental-output/${RELEASE}/
                    gsutil cp output/merged/monarch-kg.nt.gz gs://monarch-ingest/experimental-output/${RELEASE}/
                    gsutil cp merged_graph_stats.yaml gs://monarch-ingest/experimental-output/${RELEASE}/
                '''
            }
        }
    }
}
