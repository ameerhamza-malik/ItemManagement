# Flask ItemManagement - Security Enhancements

**Project:** ItemManagement  
**Date:** October 29, 2025  
**Author:** Malik Ameer Hamza  
**Roll No:** 22i-1570

## Overview

This Flask application implements comprehensive security best practices to protect against common web vulnerabilities including SQL injection, XSS attacks, CSRF attacks, and insecure authentication.

---

## Security Features Implemented

### 1. Secure Input Handling with WTForms

**Implementation:** `forms.py`

- **Custom Validators:** Created `reject_malicious_input()` validator to detect and block SQL injection and XSS attack patterns
- **Input Sanitization:** Applied `strip_filter()` to trim whitespace from all user inputs
- **Length Constraints:** Enforced maximum field lengths (Title: 250 chars, Description: 5000 chars)
- **Email Validation:** Used WTForms Email validator for proper email format checking
- **Password Policies:** Minimum 8 characters with confirmation matching

**Forms Created:**
- `ItemForm` - For creating and editing items with validation
- `RegistrationForm` - User registration with email and password confirmation
- `LoginForm` - Secure login with input validation

**Attack Patterns Blocked:**
- SQL injection keywords: `UNION SELECT`, `DROP TABLE`, `INSERT INTO`, etc.
- XSS patterns: `<script>`, `javascript:`, `onerror=`, `<iframe>`, etc.
- SQL comments and malformed queries

---

### 2. Parameterized Queries (SQL Injection Prevention)

**Implementation:** `app.py` - All database operations

Every database query uses parameterized statements with bound parameters:

```python
# Example: User lookup
db.execute('SELECT * FROM users WHERE username = ?', (username,))

# Example: Item creation
db.execute('INSERT INTO items (title, description, user_id) VALUES (?, ?, ?)', 
           (title, description, current_user.id))

# Example: Search with multiple parameters
db.execute('SELECT * FROM items WHERE title LIKE ? OR description LIKE ?', (q, q))
```

**Benefits:**
- User input is treated as data, never as SQL code
- Prevents all SQL injection attacks
- Database driver handles proper escaping

---

### 3. CSRF Protection

**Implementation:** `app.py` configuration and all form templates

**Configuration:**
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

**Template Integration:**
- All forms include `{{ form.hidden_tag() }}` for WTForm-managed forms
- Manual forms include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- Delete operations protected with CSRF tokens

**Protected Routes:**
- `/create` - Create items
- `/item/<id>/edit` - Edit items  
- `/item/<id>/delete` - Delete items
- `/register` - User registration
- `/login` - User authentication

---

### 4. Secure Session Management

**Implementation:** `app.py` session configuration

```python
app.config['SESSION_COOKIE_HTTPONLY'] = True   # Prevents JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['SESSION_COOKIE_SECURE'] = False     # Set True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Session timeout
```

**Security Features:**
- **HttpOnly:** Cookies cannot be accessed via JavaScript, preventing XSS cookie theft
- **SameSite:** Prevents CSRF attacks by restricting cross-site cookie sending
- **Secure Flag:** Should be enabled in production with HTTPS
- **Session Timeout:** Automatic logout after 2 hours of inactivity
- **Secure Secret Key:** Generated using `secrets.token_hex(32)`

---

### 5. Password Security with Bcrypt

**Implementation:** `app.py` registration and login routes

**Registration (Password Hashing):**
```python
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Hash password before storage
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
           (username, email, password_hash))
```

**Login (Password Verification):**
```python
# Verify password securely
if bcrypt.check_password_hash(user_data['password_hash'], password):
    login_user(user)
```

**Benefits:**
- Passwords never stored in plaintext
- Uses bcrypt algorithm with automatic salting
- Computationally expensive to prevent brute-force attacks
- Each password has unique salt

---

### 6. User Authentication with Flask-Login

**Implementation:** `app.py` authentication routes and decorators

**Features:**
- User session management
- Login required decorator (`@login_required`) protecting sensitive routes
- User object available in templates via `current_user`
- Automatic redirect to login page for unauthenticated users

**Protected Routes:**
- `/create` - Only authenticated users can create items
- `/item/<id>/edit` - Only authenticated users can edit items
- `/item/<id>/delete` - Only authenticated users can delete items

**User Model:**
```python
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
```

---

### 7. Custom Error Handlers

**Implementation:** `app.py` error handlers and `templates/errors/`

**Error Pages Created:**
- `404.html` - Page not found (prevents path disclosure)
- `500.html` - Internal server error (prevents stack trace exposure)

```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
```

**Security Benefits:**
- No stack traces exposed to users
- No internal file paths revealed
- No database error details leaked
- User-friendly error messages only

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Items Table
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

---

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- Flask >= 2.0
- Flask-WTF >= 1.0.0 (CSRF protection and forms)
- Flask-Bcrypt >= 1.0.0 (Password hashing)
- Flask-Login >= 0.6.0 (User authentication)
- WTForms >= 3.0.0 (Form validation)

### 2. Run the Application
```bash
python app.py
```

The application will:
- Initialize the database with proper schema
- Run on `http://127.0.0.1:5000/`
- Create `data.db` SQLite database in the project root

### 3. First-Time Setup
1. Navigate to `/register` to create an account
2. Login with your credentials at `/login`
3. Start creating items (authentication required)

---

## Security Checklist

✅ **Secure Input Handling**
- WTForms validation with custom validators
- Input sanitization and length constraints
- SQL/XSS pattern rejection

✅ **SQL Injection Prevention**
- All queries use parameterized statements
- No string concatenation in SQL
- Bound parameters for all user inputs

✅ **CSRF Protection**
- Flask-WTF CSRFProtect enabled globally
- CSRF tokens in all forms
- POST requests protected

✅ **Secure Session Management**
- HttpOnly cookies (XSS protection)
- SameSite=Lax (CSRF protection)
- Session timeout (2 hours)
- Secure secret key

✅ **Password Security**
- Bcrypt hashing with automatic salting
- Passwords never stored in plaintext
- Secure password verification

✅ **Authentication & Authorization**
- Flask-Login session management
- Login required decorators
- User-specific operations protected

✅ **Error Handling**
- Custom 404 and 500 pages
- No stack traces exposed
- No internal details leaked

---

## Usage Guide

### Public Access
- **View Items:** Anyone can view the item list and individual items
- **Search:** Public search functionality available

### Authenticated Users Only
- **Create Items:** Click "+ Create" button in navigation (requires login)
- **Edit Items:** Click "Edit" button on any item (requires login)
- **Delete Items:** Click "Delete" button (requires login + confirmation)

### Authentication Flow
1. **Register:** `/register` - Create new account with username, email, password
2. **Login:** `/login` - Authenticate with username and password
3. **Logout:** User dropdown menu → Logout

---

## Production Deployment Recommendations

### 1. Environment Variables
```python
# Replace hardcoded values with environment variables
app.secret_key = os.environ.get('SECRET_KEY')
```

### 2. HTTPS Configuration
```python
app.config['SESSION_COOKIE_SECURE'] = True  # Enable for HTTPS
```

### 3. Database
- Use PostgreSQL or MySQL instead of SQLite
- Implement database connection pooling
- Regular backups

### 4. Additional Security
- Rate limiting for login attempts
- Email verification for registration
- Password reset functionality
- Account lockout after failed attempts
- Content Security Policy (CSP) headers

### 5. Monitoring
- Log all authentication attempts
- Monitor for suspicious patterns
- Set up alerts for security events

---

## Testing & Verification

### Manual Tests Performed
1. ✅ Form validation with invalid inputs
2. ✅ SQL injection attempt blocking
3. ✅ XSS payload rejection
4. ✅ CSRF token validation
5. ✅ Unauthenticated access blocking
6. ✅ Password hashing verification
7. ✅ Session timeout functionality
8. ✅ Error page display (404, 500)

### Test Accounts
Create test accounts via `/register` to verify:
- Registration flow
- Password hashing
- Login authentication
- Session management
- Protected route access

---

## File Structure

```
ItemManagement/
├── app.py                      # Main application with security features
├── forms.py                    # Secure form definitions with validators
├── requirements.txt            # Dependencies including security packages
├── data.db                     # SQLite database (auto-created)
├── static/
│   └── style.css              # Custom styles
└── templates/
    ├── base.html              # Base template with auth navigation
    ├── index.html             # Item listing with CSRF-protected forms
    ├── view.html              # Item detail view
    ├── edit.html              # Item edit form with WTForms
    ├── login.html             # Login page
    ├── register.html          # Registration page
    └── errors/
        ├── 404.html           # Custom 404 error page
        └── 500.html           # Custom 500 error page
```

---

## Code References

### Key Security Implementations

**1. forms.py**
- Lines 17-48: Custom validator `reject_malicious_input()`
- Lines 51-76: ItemForm with validation
- Lines 79-123: RegistrationForm with password policies
- Lines 126-147: LoginForm with input validation

**2. app.py**
- Lines 33-52: Security configuration (CSRF, Bcrypt, Session)
- Lines 86-121: User authentication system
- Lines 145-178: Registration route with bcrypt hashing
- Lines 181-209: Login route with password verification
- Lines 224-255: Create route with @login_required and validation
- Lines 271-305: Edit route with CSRF protection
- Lines 308-315: Delete route with authentication check
- Lines 318-327: Error handlers (404, 500)

**3. Templates**
- All forms: `{{ form.hidden_tag() }}` for CSRF tokens
- base.html: Conditional navigation based on `current_user.is_authenticated`
- Delete forms: Manual CSRF token inclusion

---

## Security Audit Summary

| Security Control | Status | Implementation |
|-----------------|--------|----------------|
| Input Validation | ✅ Implemented | WTForms with custom validators |
| SQL Injection Protection | ✅ Implemented | Parameterized queries everywhere |
| XSS Prevention | ✅ Implemented | Jinja2 auto-escaping + input validation |
| CSRF Protection | ✅ Implemented | Flask-WTF CSRFProtect |
| Password Security | ✅ Implemented | Bcrypt hashing |
| Session Security | ✅ Implemented | HttpOnly, SameSite, timeouts |
| Authentication | ✅ Implemented | Flask-Login with login_required |
| Error Handling | ✅ Implemented | Custom error pages |
| Authorization | ✅ Implemented | Route-level access control |

---

## Conclusion

This Flask application implements industry-standard security practices to protect against common web vulnerabilities. All user inputs are validated and sanitized, database operations use parameterized queries, passwords are securely hashed, sessions are properly managed, and CSRF protection is enabled throughout the application.

The implementation follows OWASP guidelines and Flask security best practices, making it suitable for educational purposes and as a foundation for production applications with additional hardening.

---

**Author:** Malik Ameer Hamza  
**Roll No:** 22i-1570  
**Course:** Web Security  
**Institution:** FAST NUCES
