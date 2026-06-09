pipeline {
    agent any

    environment {
        DATABASE_URL = 'sqlite:///:memory:'
        DB_URL_OVERRIDE = 'sqlite:///:memory:'
        SECRET_KEY = 'test-secret-key-for-unit-tests-only-change-in-production'
        ACCESS_TOKEN_EXPIRE_MINUTES = '30'
        REFRESH_TOKEN_EXPIRE_DAYS = '7'
        APP_NAME = 'GrindX'
        APP_VERSION = '0.1.0'
        DEBUG = 'false'
        LOG_LEVEL = 'INFO'
        CORS_ORIGINS = '["*"]'
        RATE_LIMIT_REQUESTS = '100'
        RATE_LIMIT_WINDOW_SECONDS = '60'
    }

    stages {
        stage('Setup') {
            steps {
                sh 'python3 --version'
                sh 'pip3 install ruff>=0.3.0'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r apps/api-postgres/requirements.txt'
                sh 'pip3 install -r apps/api-sqlserver/requirements.txt'
            }
        }

        stage('Lint') {
            steps {
                sh 'ruff check apps/ packages/ --select E,F,I --ignore E501'
                sh 'ruff format packages/ apps/ --check'
            }
        }

        stage('Test API Postgres') {
            steps {
                dir('apps/api-postgres') {
                    sh 'PYTHONPATH=../../packages python3 -m pytest tests/ -v --tb=short --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=70'
                }
            }
        }

        stage('Test API SQL Server') {
            steps {
                dir('apps/api-sqlserver') {
                    sh 'PYTHONPATH=../../packages python3 -m pytest tests/ -v --tb=short --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=70'
                }
            }
        }

        stage('Test Shared') {
            steps {
                dir('packages/shared') {
                    sh 'PYTHONPATH=.. python3 -m pytest tests/ -v --tb=short --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=70'
                }
            }
        }

        stage('Test Root') {
            steps {
                sh 'PYTHONPATH=apps/api-postgres:apps/api-sqlserver:packages python3 -m pytest tests/ -v --tb=short --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=70'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline concluída com sucesso!'
        }
        failure {
            echo 'Pipeline falhou. Verificar logs.'
        }
    }
}
