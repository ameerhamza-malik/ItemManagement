pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = 'venv'
        APP_NAME = 'ItemManagement'
        FLASK_ENV = 'production'
        DEPLOY_TARGET = 'C:\\Hamza\\Labs\\Lab11\\ItemManagement\\deploy_target'
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning repository...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    pytest --verbose --junit-xml=test-results.xml
                '''
            }
        }
        
        stage('Build Artifact') {
            steps {
                echo 'Building application package...'
                bat '''
                    if exist dist rmdir /s /q dist
                    mkdir dist
                    xcopy /E /I /Y static dist\\static
                    xcopy /E /I /Y templates dist\\templates
                    copy app.py dist\\
                    copy forms.py dist\\
                    copy requirements.txt dist\\
                '''
            }
        }
        
        stage('Deploy (Simulate)') {
            steps {
                echo 'Deploying application to target directory...'
                bat '''
                    if not exist "%DEPLOY_TARGET%" mkdir "%DEPLOY_TARGET%"
                    xcopy /E /I /Y dist "%DEPLOY_TARGET%"
                '''
            }
        }
    }
    
    post {
        always {
            junit testResults: 'test-results.xml', allowEmptyResults: true
        }
        success {
            echo 'Deployment successful!'
        }
    }
}
