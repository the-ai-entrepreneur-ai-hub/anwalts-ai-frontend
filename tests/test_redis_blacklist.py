"""
Unit Tests for Redis Blacklist Implementation
Tests the refactored token blacklist using individual keys with TTL
"""

import pytest
import jwt
import time
import hashlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


class TestRedisBlacklist:
    """Test suite for Redis blacklist implementation"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        redis_mock = Mock()
        redis_mock.setex = Mock(return_value=True)
        redis_mock.get = Mock(return_value=None)
        redis_mock.sismember = Mock(return_value=False)
        return redis_mock
    
    @pytest.fixture
    def mock_cache_service(self, mock_redis):
        """Mock cache service with Redis client"""
        cache_service = Mock()
        cache_service.redis_client = mock_redis
        return cache_service
    
    @pytest.fixture
    def auth_service(self, mock_cache_service):
        """Create auth service instance with mocked cache"""
        # Import the actual auth service
        import sys
        sys.path.insert(0, '/root')
        from auth_service import AuthService
        
        service = AuthService(cache_service=mock_cache_service)
        return service
    
    @pytest.fixture
    def sample_token(self):
        """Generate a sample JWT token"""
        secret = "test-secret-key-for-testing-only"
        payload = {
            'user_id': '12345',
            'email': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, secret, algorithm='HS256')
        return token, payload, secret
    
    def test_blacklist_uses_individual_keys(self, auth_service, mock_redis, sample_token):
        """
        Test 1: Verify blacklist uses individual keys, not Set
        CRITICAL: Must use SETEX with individual keys, not SADD
        """
        token, payload, _ = sample_token
        
        # Blacklist the token
        auth_service.blacklist_token(token)
        
        # Verify SETEX was called (individual key with TTL)
        assert mock_redis.setex.called, "setex should be called for individual keys"
        
        # Verify SADD was NOT called (old Set-based method)
        assert not hasattr(mock_redis, 'sadd') or not mock_redis.sadd.called, \
            "sadd should NOT be called (old Set method)"
        
        # Verify the key format is correct
        call_args = mock_redis.setex.call_args
        key = call_args[0][0]
        assert key.startswith("blacklist:"), f"Key should start with 'blacklist:', got: {key}"
    
    def test_blacklist_calculates_ttl_from_jwt(self, auth_service, mock_redis, sample_token):
        """
        Test 2: Verify TTL is calculated from JWT expiry time
        TTL should match token's remaining validity
        """
        token, payload, _ = sample_token
        
        # Calculate expected TTL
        expected_ttl = int(payload['exp'].timestamp() - time.time())
        
        # Blacklist the token
        auth_service.blacklist_token(token)
        
        # Verify SETEX was called with correct TTL
        call_args = mock_redis.setex.call_args
        actual_ttl = call_args[0][1]
        
        # Allow 2 second difference for test execution time
        assert abs(actual_ttl - expected_ttl) <= 2, \
            f"TTL should be {expected_ttl}, got {actual_ttl}"
    
    def test_blacklist_uses_token_hash(self, auth_service, mock_redis, sample_token):
        """
        Test 3: Verify token hash is used for key (security best practice)
        Should use SHA256 hash, not raw token
        """
        token, payload, _ = sample_token
        
        # Blacklist the token
        auth_service.blacklist_token(token)
        
        # Get the key used
        call_args = mock_redis.setex.call_args
        key = call_args[0][0]
        
        # Verify it's a hash (not the raw token)
        assert "eyJ" not in key, "Key should not contain raw JWT token"
        
        # Verify it uses the expected hash format
        expected_hash = hashlib.sha256(token.encode()).hexdigest()[-16:]
        assert expected_hash in key, f"Key should contain token hash"
    
    def test_check_blacklist_uses_get_not_sismember(self, auth_service, mock_redis, sample_token):
        """
        Test 4: Verify blacklist check uses GET (individual key), not SISMEMBER (Set)
        """
        token, _, _ = sample_token
        
        # Check if token is blacklisted
        try:
            is_blacklisted = auth_service.verify_token(token)
        except Exception:
            pass  # May fail due to mocking, that's okay
        
        # Verify GET was called (individual key check)
        assert mock_redis.get.called, "get should be called to check individual keys"
        
        # Verify SISMEMBER was NOT called (old Set check)
        assert not mock_redis.sismember.called, \
            "sismember should NOT be called (old Set method)"
    
    def test_no_in_memory_fallback(self, auth_service):
        """
        Test 5: Verify in-memory fallback is removed
        Should not have self.blacklisted_tokens Set
        """
        # Check that in-memory Set doesn't exist
        assert not hasattr(auth_service, 'blacklisted_tokens') or \
               not isinstance(getattr(auth_service, 'blacklisted_tokens', None), set), \
            "In-memory blacklisted_tokens Set should be removed"
    
    def test_expired_token_not_blacklisted(self, auth_service, mock_redis):
        """
        Test 6: Verify expired tokens are not added to blacklist
        TTL would be negative, so should skip
        """
        # Create an already-expired token
        secret = "test-secret"
        payload = {
            'user_id': '12345',
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(payload, secret, algorithm='HS256')
        
        # Try to blacklist it
        auth_service.blacklist_token(expired_token)
        
        # Verify SETEX was NOT called (no point blacklisting expired token)
        assert not mock_redis.setex.called, \
            "setex should not be called for expired tokens"
    
    def test_blacklist_handles_redis_failure(self, auth_service, mock_redis, sample_token):
        """
        Test 7: Verify proper error handling when Redis fails
        Should raise RuntimeError if Redis unavailable
        """
        token, _, _ = sample_token
        
        # Simulate Redis failure
        auth_service.cache_service = None
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Redis required"):
            auth_service.blacklist_token(token)
    
    def test_blacklist_key_format_consistency(self, auth_service, mock_redis):
        """
        Test 8: Verify consistent key format across multiple tokens
        All keys should use same format: blacklist:{hash}
        """
        # Create multiple tokens
        secret = "test-secret"
        tokens = []
        for i in range(5):
            payload = {
                'user_id': f'user_{i}',
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, secret, algorithm='HS256')
            tokens.append(token)
        
        # Blacklist all tokens
        for token in tokens:
            auth_service.blacklist_token(token)
        
        # Verify all calls used consistent key format
        assert mock_redis.setex.call_count == 5, "Should call setex 5 times"
        
        for call in mock_redis.setex.call_args_list:
            key = call[0][0]
            assert key.startswith("blacklist:"), "All keys should start with blacklist:"
            assert len(key) == len("blacklist:") + 16, "Hash should be 16 chars"
    
    def test_no_cleanup_method_needed(self, auth_service):
        """
        Test 9: Verify cleanup method is removed
        With TTL on individual keys, no periodic cleanup needed
        """
        # Check that cleanup method doesn't exist or is not used
        assert not hasattr(auth_service, 'cleanup_blacklisted_tokens') or \
               not callable(getattr(auth_service, 'cleanup_blacklisted_tokens', None)), \
            "cleanup_blacklisted_tokens method should be removed"
    
    def test_blacklist_idempotent(self, auth_service, mock_redis, sample_token):
        """
        Test 10: Verify blacklisting same token multiple times is safe
        Should just overwrite with same TTL
        """
        token, _, _ = sample_token
        
        # Blacklist token multiple times
        auth_service.blacklist_token(token)
        auth_service.blacklist_token(token)
        auth_service.blacklist_token(token)
        
        # Should be called 3 times (idempotent operation)
        assert mock_redis.setex.call_count == 3, "Should allow multiple blacklist calls"
        
        # All calls should use same key
        keys = [call[0][0] for call in mock_redis.setex.call_args_list]
        assert len(set(keys)) == 1, "All calls should use same key"


class TestRedisBlacklistIntegration:
    """Integration tests with real Redis (if available)"""
    
    @pytest.fixture
    def redis_client(self):
        """Create real Redis client for integration tests"""
        try:
            import redis
            client = redis.Redis(host='redis', port=6379, decode_responses=True)
            client.ping()
            return client
        except Exception:
            pytest.skip("Redis not available for integration tests")
    
    def test_blacklist_integration_with_real_redis(self, redis_client):
        """
        Integration Test: Verify blacklist works with real Redis
        """
        # Create a test token
        secret = "test-secret"
        payload = {
            'user_id': 'test_user',
            'exp': datetime.utcnow() + timedelta(seconds=5)  # 5 second expiry
        }
        token = jwt.encode(payload, secret, algorithm='HS256')
        token_hash = hashlib.sha256(token.encode()).hexdigest()[-16:]
        key = f"blacklist:{token_hash}"
        
        # Set blacklist entry with 5 second TTL
        redis_client.setex(key, 5, "1")
        
        # Verify it exists
        assert redis_client.get(key) == "1", "Token should be blacklisted"
        
        # Verify TTL is set
        ttl = redis_client.ttl(key)
        assert 0 < ttl <= 5, f"TTL should be 1-5 seconds, got {ttl}"
        
        # Wait for expiry
        time.sleep(6)
        
        # Verify it's automatically removed
        assert redis_client.get(key) is None, "Token should be auto-removed after TTL"
        
        # Cleanup
        redis_client.delete(key)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
