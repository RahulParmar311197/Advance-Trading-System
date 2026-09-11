import pytest

from packages.saas.auth import APIKeyAuthenticator, APIKeyRecord, Principal, Role, authorize


def test_api_key_authentication_returns_scoped_principal_without_exposing_secret():
    secret = "test-secret"
    record = APIKeyRecord(
        key_id="key-1",
        organization_id="org-1",
        user_id="user-1",
        role=Role.RESEARCHER,
        secret_digest=APIKeyAuthenticator.digest_secret(secret),
    )
    principal = APIKeyAuthenticator({record.key_id: record}).authenticate("key-1", secret)
    assert principal == Principal("user-1", "org-1", Role.RESEARCHER)
    assert secret not in record.secret_digest


def test_invalid_or_inactive_api_key_fails_closed():
    secret = "test-secret"
    record = APIKeyRecord(
        key_id="key-1",
        organization_id="org-1",
        user_id="user-1",
        role=Role.TRADER,
        secret_digest=APIKeyAuthenticator.digest_secret(secret),
        active=False,
    )
    authenticator = APIKeyAuthenticator({record.key_id: record})
    with pytest.raises(PermissionError, match="invalid API key"):
        authenticator.authenticate("key-1", secret)
    with pytest.raises(PermissionError, match="invalid API key"):
        authenticator.authenticate("missing", secret)


def test_role_and_organization_authorization_are_enforced():
    principal = Principal("user-1", "org-1", Role.RESEARCHER)
    authorize(principal, "research", "org-1")
    with pytest.raises(PermissionError, match="permission denied"):
        authorize(principal, "trade", "org-1")
    with pytest.raises(PermissionError, match="organization scope"):
        authorize(principal, "research", "org-2")


def test_digest_rejects_empty_secret():
    with pytest.raises(ValueError, match="non-empty"):
        APIKeyAuthenticator.digest_secret("")
