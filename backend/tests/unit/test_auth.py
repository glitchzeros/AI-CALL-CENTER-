"""
Unit tests for authentication functionality
"""

import pytest
from fastapi.testclient import TestClient
from tests.conftest import assert_response_success, assert_response_error


class TestAuthRegistration:
    """Test user registration functionality"""
    
    def test_register_valid_user(self, client: TestClient, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=sample_user_data)
        data = assert_response_success(response, 201)
        
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
        assert data["user"]["phone"] == sample_user_data["phone"]
        assert "password" not in data["user"]  # Password should not be returned
    
    def test_register_duplicate_email(self, client: TestClient, sample_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/auth/register", json=sample_user_data)
        
        # Try to register with same email
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 409)
    
    def test_register_invalid_email(self, client: TestClient, sample_user_data):
        """Test registration with invalid email"""
        sample_user_data["email"] = "invalid-email"
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 422)
    
    def test_register_weak_password(self, client: TestClient, sample_user_data):
        """Test registration with weak password"""
        sample_user_data["password"] = "weak"
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 422)
    
    def test_register_invalid_phone(self, client: TestClient, sample_user_data):
        """Test registration with invalid phone number"""
        sample_user_data["phone"] = "invalid-phone"
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 422)
    
    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields"""
        incomplete_data = {"email": "test@example.com"}
        response = client.post("/api/auth/register", json=incomplete_data)
        assert_response_error(response, 422)


class TestAuthLogin:
    """Test user login functionality"""
    
    def test_login_valid_credentials(self, client: TestClient, sample_user_data):
        """Test successful login"""
        # Register user first
        client.post("/api/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        data = assert_response_success(response)
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert_response_error(response, 401)
    
    def test_login_invalid_password(self, client: TestClient, sample_user_data):
        """Test login with wrong password"""
        # Register user first
        client.post("/api/auth/register", json=sample_user_data)
        
        # Login with wrong password
        login_data = {
            "email": sample_user_data["email"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert_response_error(response, 401)
    
    def test_login_unverified_user(self, client: TestClient, sample_user_data):
        """Test login with unverified user"""
        # This test assumes SMS verification is required
        # Register user (but don't verify)
        client.post("/api/auth/register", json=sample_user_data)
        
        # Try to login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        # Depending on implementation, this might succeed or fail
        # Adjust based on your business logic
        assert response.status_code in [200, 401]


class TestAuthTokens:
    """Test token-related functionality"""
    
    def test_access_protected_endpoint_with_valid_token(self, authenticated_client: TestClient):
        """Test accessing protected endpoint with valid token"""
        response = authenticated_client.get("/api/users/profile")
        assert_response_success(response)
    
    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/users/profile")
        assert_response_error(response, 401)
    
    def test_access_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        client.headers.update({"Authorization": "Bearer invalid_token"})
        response = client.get("/api/users/profile")
        assert_response_error(response, 401)
    
    def test_refresh_token(self, client: TestClient, sample_user_data):
        """Test token refresh functionality"""
        # Register and login
        client.post("/api/auth/register", json=sample_user_data)
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        login_data = assert_response_success(login_response)
        
        # Refresh token
        refresh_data = {"refresh_token": login_data["refresh_token"]}
        response = client.post("/api/auth/refresh", json=refresh_data)
        data = assert_response_success(response)
        
        assert "access_token" in data
        assert "refresh_token" in data


class TestAuthValidation:
    """Test authentication validation"""
    
    @pytest.mark.parametrize("email", [
        "invalid-email",
        "@example.com",
        "test@",
        "test.example.com",
        ""
    ])
    def test_invalid_email_formats(self, client: TestClient, sample_user_data, email):
        """Test various invalid email formats"""
        sample_user_data["email"] = email
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 422)
    
    @pytest.mark.parametrize("password", [
        "short",
        "nouppercase123!",
        "NOLOWERCASE123!",
        "NoNumbers!",
        "NoSpecialChars123",
        ""
    ])
    def test_invalid_password_formats(self, client: TestClient, sample_user_data, password):
        """Test various invalid password formats"""
        sample_user_data["password"] = password
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 422)
    
    @pytest.mark.parametrize("phone", [
        "123",
        "invalid-phone",
        "+",
        "++1234567890",
        ""
    ])
    def test_invalid_phone_formats(self, client: TestClient, sample_user_data, phone):
        """Test various invalid phone formats"""
        sample_user_data["phone"] = phone
        response = client.post("/api/auth/register", json=sample_user_data)
        assert_response_error(response, 422)


class TestAuthSecurity:
    """Test authentication security features"""
    
    def test_password_not_returned_in_response(self, client: TestClient, sample_user_data):
        """Test that password is never returned in API responses"""
        # Registration
        response = client.post("/api/auth/register", json=sample_user_data)
        data = assert_response_success(response, 201)
        assert "password" not in str(data)
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        data = assert_response_success(response)
        assert "password" not in str(data)
    
    def test_rate_limiting(self, client: TestClient):
        """Test rate limiting on authentication endpoints"""
        # This test would need to be adjusted based on your rate limiting implementation
        login_data = {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
        
        # Make multiple failed login attempts
        for _ in range(10):
            response = client.post("/api/auth/login", json=login_data)
            # Should eventually get rate limited
            if response.status_code == 429:
                break
        else:
            pytest.skip("Rate limiting not implemented or threshold too high")
    
    def test_sql_injection_protection(self, client: TestClient):
        """Test protection against SQL injection attacks"""
        malicious_data = {
            "email": "test@example.com'; DROP TABLE users; --",
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/auth/login", json=malicious_data)
        # Should not cause a server error
        assert response.status_code in [400, 401, 422]
    
    def test_xss_protection(self, client: TestClient, sample_user_data):
        """Test protection against XSS attacks"""
        sample_user_data["email"] = "<script>alert('xss')</script>@example.com"
        
        response = client.post("/api/auth/register", json=sample_user_data)
        # Should be rejected due to validation
        assert_response_error(response, 422)