from security import create_access_token, verify_access_token


def test_token_creation_and_verification():
    user_id = 123

    token = create_access_token(user_id)

    verified_user_id = verify_access_token(token)

    assert verified_user_id == user_id


def test_invalid_token():
    try:
        verify_access_token("invalid.token.value")
        assert False, "Invalid token should be rejected"

    except ValueError:
        assert True