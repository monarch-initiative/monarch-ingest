pipeline {
    agent none
    environment {
        HOME = "${env.WORKSPACE}"
    }
    stages {
        stage('setup') {
            agent { dockerfile true }
            steps {
                sh '''
                $HOME/.poetry/bin/poetry install
                '''
            }
        }
        stage('download') {
            agent { label 'worker'}
            steps {
                sh 'gsutil -m cp -r data-cache/data .'
            }
        }
        stage('transform') {
            agent { dockerfile true }
            steps {
                sh '''
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/alliance/gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/alliance/gene_to_phenotype.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/alliance/publication.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/ctd/chemical_to_disease.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/flybase/publication_to_gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/goa/go_annotation.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/hgnc/gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/hpoa/disease_phenotype.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/mgi/publication_to_gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/omim/gene_to_disease.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/panther/ref_genome_orthologs.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/pombase/gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/pombase/gene_to_phenotype.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/reactome/chemical_to_pathway.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/reactome/gene_to_pathway.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/rgd/publication_to_gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/sgd/publication_to_gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/string/protein_links.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/xenbase/gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/xenbase/gene_to_phenotype.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/xenbase/publication_to_gene.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/zfin/gene_to_phenotype.yaml --row-limit 1000
                    $HOME/.poetry/bin/poetry run koza transform --source monarch_ingest/zfin/publication_to_gene.yaml --row-limit 1000
                '''
            }
        }
        stage('upload') {
            agent { label 'worker'}
            steps {
                sh 'gsutil -m cp -r output/*.tsv gs://monarch-ingest/experimental-output/'
                sh 'gsutil -m cp -r output/*.yaml gs://monarch-ingest/experimental-output/'
            }
        }
    }
}
