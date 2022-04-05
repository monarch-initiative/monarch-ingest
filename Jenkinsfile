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
                    poetry run koza transform --source monarch_ingest/alliance/gene.yaml
                    poetry run koza transform --source monarch_ingest/alliance/gene_to_phenotype.yaml
                    poetry run koza transform --source monarch_ingest/alliance/publication.yaml
                    poetry run koza transform --source monarch_ingest/ctd/chemical_to_disease.yaml
                    poetry run koza transform --source monarch_ingest/flybase/publication_to_gene.yaml
                    poetry run koza transform --source monarch_ingest/goa/go_annotation.yaml
                    poetry run koza transform --source monarch_ingest/hgnc/gene.yaml
                    poetry run koza transform --source monarch_ingest/hpoa/disease_phenotype.yaml
                    poetry run koza transform --source monarch_ingest/mgi/publication_to_gene.yaml
                    poetry run koza transform --source monarch_ingest/omim/gene_to_disease.yaml
                    poetry run koza transform --source monarch_ingest/panther/ref_genome_orthologs.yaml
                    poetry run koza transform --source monarch_ingest/pombase/gene.yaml
                    poetry run koza transform --source monarch_ingest/pombase/gene_to_phenotype.yaml
                    poetry run koza transform --source monarch_ingest/reactome/chemical_to_pathway.yaml
                    poetry run koza transform --source monarch_ingest/reactome/gene_to_pathway.yaml
                    poetry run koza transform --source monarch_ingest/rgd/publication_to_gene.yaml
                    poetry run koza transform --source monarch_ingest/sgd/publication_to_gene.yaml
                    poetry run koza transform --source monarch_ingest/string/protein_links.yaml
                    poetry run koza transform --source monarch_ingest/xenbase/gene.yaml
                    poetry run koza transform --source monarch_ingest/xenbase/gene_to_phenotype.yaml
                    poetry run koza transform --source monarch_ingest/xenbase/publication_to_gene.yaml
                    poetry run koza transform --source monarch_ingest/zfin/gene_to_phenotype.yaml
                    poetry run koza transform --source monarch_ingest/zfin/publication_to_gene.yaml
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
