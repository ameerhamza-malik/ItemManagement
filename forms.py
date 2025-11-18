"""
Secure Forms with Input Validation and Sanitization
Author: Malik Ameer Hamza
Roll No: 22i-1570
Date: October 29, 2025

This module implements WTForms with custom validators and filters
to prevent SQL injection, XSS attacks, and enforce input constraints.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo
import re


# Custom filter to trim whitespace
def strip_filter(value):
    """Strip leading and trailing whitespace from input"""
    return value.strip() if value else value


# Custom validator to detect and reject malicious SQL/XSS payloads
def reject_malicious_input(form, field):
    """
    Reject obvious SQL injection and XSS attack patterns.
    This is a defense-in-depth measure alongside parameterized queries.
    """
    if not field.data:
        return

    suspicious_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"<iframe",
        r"--\s*$",  # SQL comment
        r";\s*DROP",
        r"'\s*(OR|AND)\s*'?\d*'?\s*=\s*'?\d*",  # ' OR '1'='1
    ]

    data_upper = field.data.upper()
    for pattern in suspicious_patterns:
        if re.search(pattern, data_upper, re.IGNORECASE):
            raise ValidationError(
                "Invalid input detected. Please remove special characters or SQL/script keywords.")


class ItemForm(FlaskForm):
    """
    Secure form for creating and editing items.
    Includes length constraints, trimming, and malicious input rejection.
    """
    title = StringField(
        'Title',
        validators=[
            DataRequired(
                message="Title is required."),
            Length(
                min=1,
                max=250,
                message="Title must be between 1 and 250 characters."),
            reject_malicious_input],
        filters=[strip_filter],
        render_kw={
            "class": "form-control",
            "required": True,
            "maxlength": "250"})

    description = TextAreaField(
        'Description',
        validators=[
            Length(
                max=5000,
                message="Description must not exceed 5000 characters."),
            reject_malicious_input],
        filters=[strip_filter],
        render_kw={
            "class": "form-control",
            "rows": "4"})

    submit = SubmitField('Submit', render_kw={"class": "btn btn-primary"})


class RegistrationForm(FlaskForm):
    """
    Secure registration form with email validation and password confirmation.
    Enforces strong password policies and prevents malicious usernames.
    """
    username = StringField(
        'Username',
        validators=[
            DataRequired(
                message="Username is required."),
            Length(
                min=3,
                max=50,
                message="Username must be between 3 and 50 characters."),
            reject_malicious_input],
        filters=[strip_filter],
        render_kw={
            "class": "form-control",
            "required": True,
            "maxlength": "50"})

    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email address."),
            Length(max=120, message="Email must not exceed 120 characters.")
        ],
        filters=[strip_filter],
        render_kw={"class": "form-control", "required": True, "type": "email"}
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(
                message="Password is required."),
            Length(
                min=8,
                max=128,
                message="Password must be between 8 and 128 characters.")],
        render_kw={
            "class": "form-control",
            "required": True,
            "type": "password"})

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ],
        render_kw={"class": "form-control", "required": True, "type": "password"}
    )

    submit = SubmitField(
        'Register', render_kw={
            "class": "btn btn-primary w-100"})


class LoginForm(FlaskForm):
    """
    Secure login form with input validation.
    """
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required."),
            Length(max=50)
        ],
        filters=[strip_filter],
        render_kw={"class": "form-control", "required": True}
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(
                message="Password is required.")],
        render_kw={
            "class": "form-control",
            "required": True,
            "type": "password"})

    submit = SubmitField('Login', render_kw={"class": "btn btn-primary w-100"})
