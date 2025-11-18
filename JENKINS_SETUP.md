# Jenkins Pipeline Setup Guide
## ItemManagement Secure Flask Application

**Author:** Malik Ameer Hamza  
**Roll No:** 22i-1570  
**Date:** November 18, 2025

---

## Overview

This Jenkins pipeline automates the build, test, and deployment process for the ItemManagement Flask application with integrated security scanning and quality checks.

---

## Pipeline Stages

### 1. **Checkout**
- Fetches the latest code from the Git repository
- Uses `checkout scm` for automatic repository detection

### 2. **Setup Python Environment**
- Creates a Python virtual environment
- Upgrades pip to the latest version
- Verifies Python installation

### 3. **Install Dependencies**
- Installs all required packages from `requirements.txt`
- Includes Flask, Flask-WTF, Flask-Bcrypt, Flask-Login, WTForms

### 4. **Security Scan - Dependencies**
- Uses **Safety** to check for known vulnerabilities in dependencies
- Generates JSON report of vulnerable packages
- Continues pipeline even if vulnerabilities found (with warning)

### 5. **Code Quality - Linting**
- Runs **Flake8** for PEP 8 compliance
- Runs **Pylint** for code quality metrics
- Checks `app.py` and `forms.py` for issues

### 6. **Security Scan - SAST**
- Uses **Bandit** for static application security testing
- Scans Python code for common security issues:
  - SQL injection vulnerabilities
  - Command injection risks
  - Hardcoded passwords
  - Weak cryptography usage
- Generates `bandit-report.json`

### 7. **Run Tests**
- Executes pytest test suite
- Generates JUnit XML test results
- Tests input validation, authentication, CSRF protection

### 8. **Database Migration Check**
- Initializes database schema
- Verifies table creation (items, users)
- Checks column migrations

### 9. **Build Artifact**
- Creates `dist/` directory with deployment files
- Copies application code, templates, static files
- Includes documentation (SECURITY_REPORT.md, QUICKSTART.md)

### 10. **Security Configuration Check**
- Verifies all security features are enabled:
  - CSRF Protection
  - Bcrypt password hashing
  - Flask-Login authentication
- Fails build if security features missing

### 11. **Archive Artifacts**
- Archives build artifacts for deployment
- Stores security scan reports
- Saves test results for analysis

---

## Jenkins Setup Instructions

### Prerequisites

1. **Jenkins Installation**
   - Jenkins 2.x or higher
   - Windows/Linux/macOS compatible

2. **Required Jenkins Plugins**
   ```
   - Git Plugin
   - Pipeline Plugin
   - Email Extension Plugin (for notifications)
   - JUnit Plugin (for test reports)
   - Warnings Next Generation Plugin (for code quality)
   ```

3. **System Requirements**
   - Python 3.8+ installed on Jenkins agent
   - Git installed
   - Access to repository (GitHub/GitLab/Bitbucket)

---

## Creating the Jenkins Job

### Step 1: Create New Pipeline Job

1. Open Jenkins dashboard
2. Click **"New Item"**
3. Enter job name: `ItemManagement-Pipeline`
4. Select **"Pipeline"**
5. Click **"OK"**

### Step 2: Configure Source Code Management

1. In **Pipeline** section, select:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/ameerhamza-malik/ItemManagement.git`
   - **Branch:** `*/main`
   - **Script Path:** `Jenkinsfile`

2. Click **"Save"**

### Step 3: Configure Build Triggers (Optional)

Choose one or more:

- **GitHub hook trigger for GITScm polling** - Trigger on push
- **Poll SCM** - Schedule: `H/15 * * * *` (every 15 minutes)
- **Build periodically** - Schedule: `H 2 * * *` (daily at 2 AM)

### Step 4: Configure Email Notifications

1. Go to **Manage Jenkins** → **Configure System**
2. Find **Extended E-mail Notification**
3. Configure SMTP settings:
   ```
   SMTP Server: smtp.gmail.com
   SMTP Port: 587
   Use SSL: Yes
   ```
4. Update email addresses in `Jenkinsfile`:
   ```groovy
   to: 'your-email@example.com'
   ```

---

## Environment Variables

Configure in Jenkins job or system:

```groovy
PYTHON_VERSION = '3.9'       // Python version
VENV_DIR = 'venv'           // Virtual environment directory
APP_NAME = 'ItemManagement' // Application name
FLASK_ENV = 'production'    // Flask environment
```

---

## Running the Pipeline

### Manual Build

1. Open the Jenkins job
2. Click **"Build Now"**
3. Monitor progress in **"Build History"**
4. View console output for details

### Automated Builds

Pipeline triggers automatically on:
- Git push (if webhook configured)
- Scheduled intervals
- Manual trigger

---

## Pipeline Outputs

### 1. **Console Log**
- Real-time build output
- Stage-by-stage execution details
- Error messages and warnings

### 2. **Test Results**
- JUnit test report
- Pass/fail statistics
- Test execution trends

### 3. **Artifacts**
- `dist/` - Deployment package
- `bandit-report.json` - Security scan results
- `test-results.xml` - Test execution results

### 4. **Email Notifications**
- Success/failure notifications
- Build summary
- Security feature verification status

---

## Security Checks Performed

| Check | Tool | Purpose |
|-------|------|---------|
| Dependency Vulnerabilities | Safety | Known CVEs in packages |
| Code Quality | Flake8, Pylint | PEP 8 compliance, code smells |
| Security Issues | Bandit | SQL injection, XSS, weak crypto |
| Configuration | Custom Script | Verify security features enabled |

---

## Troubleshooting

### Issue: Python not found
**Solution:**
```groovy
environment {
    PATH = "C:\\Python39;C:\\Python39\\Scripts;${env.PATH}"
}
```

### Issue: Virtual environment activation fails
**Solution:** Use full path to Python:
```bat
C:\\Python39\\python.exe -m venv venv
```

### Issue: Dependencies installation fails
**Solution:** Clear pip cache:
```bat
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### Issue: Database initialization fails
**Solution:** Ensure data.db is writable:
```bat
if exist data.db del data.db
```

### Issue: Tests fail
**Solution:** Check test prerequisites:
- Virtual environment activated
- All dependencies installed
- Database initialized

---

## Extending the Pipeline

### Add Code Coverage

```groovy
stage('Code Coverage') {
    steps {
        bat '''
            call %VENV_DIR%\\Scripts\\activate.bat
            pip install pytest-cov
            pytest --cov=app --cov=forms --cov-report=xml --cov-report=html
        '''
    }
}
```

### Add Docker Build

```groovy
stage('Build Docker Image') {
    steps {
        bat '''
            docker build -t itemmanagement:${BUILD_NUMBER} .
            docker tag itemmanagement:${BUILD_NUMBER} itemmanagement:latest
        '''
    }
}
```

### Add Deployment Stage

```groovy
stage('Deploy to Staging') {
    when {
        branch 'main'
    }
    steps {
        bat '''
            xcopy /E /I /Y dist\\* C:\\Deploy\\ItemManagement\\
            call C:\\Deploy\\ItemManagement\\restart-service.bat
        '''
    }
}
```

---

## Best Practices

### 1. **Version Control**
- Keep `Jenkinsfile` in repository root
- Use environment variables for configuration
- Document pipeline changes in commit messages

### 2. **Security**
- Never hardcode credentials in Jenkinsfile
- Use Jenkins credentials plugin
- Scan dependencies regularly

### 3. **Notifications**
- Configure email alerts for failures
- Send summary reports to team
- Alert on security vulnerabilities

### 4. **Artifact Management**
- Archive only necessary files
- Clean old builds regularly
- Keep security reports for audit

### 5. **Performance**
- Use parallel stages when possible
- Cache dependencies
- Optimize test execution

---

## Pipeline Metrics

Track these metrics in Jenkins:

- **Build Success Rate** - Percentage of successful builds
- **Build Duration** - Time to complete pipeline
- **Test Pass Rate** - Percentage of passing tests
- **Security Issues** - Count of vulnerabilities found
- **Code Quality Score** - Linting and complexity metrics

---

## Integration with Git

### Webhook Setup (GitHub)

1. Go to repository **Settings** → **Webhooks**
2. Click **Add webhook**
3. **Payload URL:** `http://your-jenkins-url/github-webhook/`
4. **Content type:** `application/json`
5. **Events:** Just the push event
6. Click **Add webhook**

### Webhook Setup (GitLab)

1. Go to **Settings** → **Integrations**
2. **URL:** `http://your-jenkins-url/project/ItemManagement-Pipeline`
3. **Trigger:** Push events
4. Click **Add webhook**

---

## Sample Build Output

```
Started by user Malik Ameer Hamza
[Pipeline] Start of Pipeline
[Pipeline] node
[Pipeline] {
[Pipeline] stage (Checkout)
[Pipeline] {
✓ Checking out code from repository...
}
[Pipeline] stage (Setup Python Environment)
[Pipeline] {
✓ Setting up Python virtual environment...
Python 3.9.7
}
[Pipeline] stage (Install Dependencies)
[Pipeline] {
✓ Installing Python dependencies...
Successfully installed Flask-2.3.0 Flask-WTF-1.2.0 ...
}
[Pipeline] stage (Security Scan - Dependencies)
[Pipeline] {
✓ Scanning dependencies for known vulnerabilities...
All packages secure!
}
[Pipeline] stage (Run Tests)
[Pipeline] {
✓ Running unit tests...
====== 12 passed in 2.34s ======
}
[Pipeline] stage (Security Configuration Check)
[Pipeline] {
✓ Verifying security configurations...
✓ All security features enabled
}
[Pipeline] stage (Archive Artifacts)
[Pipeline] {
✓ Archiving build artifacts...
}
[Pipeline] }
✓ Build successful! All security checks passed.
Finished: SUCCESS
```

---

## Maintenance

### Regular Tasks

1. **Weekly:**
   - Review build failures
   - Update dependencies
   - Check security reports

2. **Monthly:**
   - Update Jenkins plugins
   - Review pipeline efficiency
   - Update documentation

3. **Quarterly:**
   - Security audit
   - Performance optimization
   - Pipeline refactoring

---

## Support

For issues or questions:
- Check Jenkins console logs
- Review `SECURITY_REPORT.md` for security details
- Contact: Malik Ameer Hamza (22i-1570)

---

## References

- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Bandit Security Tool](https://bandit.readthedocs.io/)
- [Safety Package Scanner](https://pyup.io/safety/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

**Author:** Malik Ameer Hamza  
**Institution:** FAST NUCES  
**Course:** Web Security / DevOps
