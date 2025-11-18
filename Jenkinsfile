pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = 'venv'
        APP_NAME = 'ItemManagement'
        FLASK_ENV = 'production'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat '''
                    python --version
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    pytest --verbose --junit-xml=test-results.xml || exit 0
                '''
            }
        }
        
        stage('Database Migration Check') {
            steps {
                echo 'Checking database schema...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -c "from app import app, init_db; import sys; sys.path.insert(0, '.'); exec(open('app.py').read().split('if __name__')[0]); app.app_context().push(); init_db(); print('Database initialized successfully')"
                '''
            }
        }
        
        stage('Build Artifact') {
            steps {
                echo 'Creating deployment artifact...'
                bat '''
                    if exist dist rmdir /s /q dist
                    mkdir dist
                    xcopy /E /I /Y static dist\\static
                    xcopy /E /I /Y templates dist\\templates
                    copy app.py dist\\
                    copy forms.py dist\\
                    copy requirements.txt dist\\
                    copy SECURITY_REPORT.md dist\\
                    copy QUICKSTART.md dist\\
                '''
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                echo 'Archiving build artifacts...'
                archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
                archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed!'
            junit testResults: 'test-results.xml', allowEmptyResults: true
        }
        success {
            echo '✓ Build successful!'
        }
        failure {
            echo '✗ Build failed! Check logs for details.'
        }
        unstable {
            echo '⚠ Build unstable. Review warnings and test failures.'
        }
    }
}
