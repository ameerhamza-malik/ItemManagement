# Flask ItemManagement - Quick Start Guide

## Installation

1. **Install all security dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   - Open browser: `http://127.0.0.1:5000/`

## First Steps

### 1. Create an Account
- Navigate to **Register** (top-right navigation)
- Fill in:
  - Username (3-50 characters)
  - Email (valid email format)
  - Password (minimum 8 characters)
  - Confirm Password
- Your password will be securely hashed with bcrypt

### 2. Login
- Click **Login** in navigation
- Enter your username and password
- Session will expire after 2 hours of inactivity

### 3. Create Items (Requires Authentication)
- Click **+ Create** button in navigation
- Fill in:
  - Title (required, max 250 chars)
  - Description (optional, max 5000 chars)
- All inputs are validated and sanitized

### 4. Manage Items
- **View:** Click any item card or "View" button
- **Edit:** Click "Edit" button (requires login)
- **Delete:** Click "Delete" button (requires login + confirmation)
- **Search:** Use search bar in navigation

## Security Features You'll Notice

✅ **CSRF Protection:** All forms include automatic CSRF tokens  
✅ **Input Validation:** Invalid inputs are rejected with clear error messages  
✅ **Authentication:** Create/Edit/Delete require login  
✅ **Secure Sessions:** Automatic logout after 2 hours  
✅ **Password Security:** Passwords are bcrypt-hashed (never stored as plaintext)  
✅ **SQL Injection Protection:** All queries use parameterized statements  
✅ **XSS Protection:** Malicious scripts are blocked  
✅ **Error Handling:** Clean error pages (no internal details exposed)  

## Testing Security

### Test Input Validation
Try creating an item with:
- Empty title → Should be rejected
- Title with `<script>alert('xss')</script>` → Should be rejected
- Title with `'; DROP TABLE items; --` → Should be rejected
- Very long inputs exceeding limits → Should be rejected

### Test Authentication
- Try accessing `/create` without login → Redirected to login page
- Try editing/deleting items without login → Redirected to login page

### Test CSRF Protection
- All POST requests require valid CSRF tokens
- Forms won't submit without proper tokens

## File Structure

```
ItemManagement/
├── app.py                    # Main Flask app with all security features
├── forms.py                  # WTForms with custom validators
├── requirements.txt          # All security dependencies
├── SECURITY_REPORT.md        # Comprehensive security documentation
├── templates/
│   ├── base.html            # Base with authentication nav
│   ├── index.html           # Item listing
│   ├── view.html            # Item details
│   ├── edit.html            # Edit form
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   └── errors/
│       ├── 404.html         # Custom 404 page
│       └── 500.html         # Custom 500 page
└── static/
    └── style.css            # Custom styles
```

## Common Issues

### Issue: Import errors for Flask extensions
**Solution:** Run `pip install -r requirements.txt` to install all dependencies

### Issue: Database doesn't exist
**Solution:** The database is auto-created on first run. Just start the app with `python app.py`

### Issue: CSRF token errors
**Solution:** Ensure your browser accepts cookies and JavaScript is enabled

## Production Deployment

⚠️ **Before deploying to production:**

1. Set `SESSION_COOKIE_SECURE = True` (requires HTTPS)
2. Use environment variable for secret key
3. Switch from SQLite to PostgreSQL/MySQL
4. Enable production logging
5. Set up rate limiting
6. Configure proper CORS policies
7. Use a production WSGI server (gunicorn, uwsgi)

## Support

For detailed security documentation, see `SECURITY_REPORT.md`

---

**Author:** Malik Ameer Hamza  
**Roll No:** 22i-1570
