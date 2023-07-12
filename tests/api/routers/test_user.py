import pytest
from api.models.user import User


@pytest.mark.anyio
async def test_create_user_api(client):
    username, password, email = "luxer", "xyz12345", "xyz@xyz.pl"

    # Verify that the user does not exist before creating
    assert await User.filter(username=username).first() is None

    data = {
        "username": username,
        "password": password,
        "email": email
    }

    response = client.post("/users/", json=data)

    assert response.status_code == 200
    user_data = response.json()

    assert user_data['uuid']
    assert user_data['username'] == username
    assert 'password' not in user_data
    assert user_data['email'] == email

    user = await User.filter(username=username).first()
    assert user.password != password

    # Check add existing user
    response = client.post("/users/", json=data)

    assert response.status_code == 422

    # Incorrect lengths
    incorrect_data = {
        "username": "luxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "password": "password",
        "email": "x@y"
    }

    response = client.post("/users/", json=incorrect_data)
    assert response.status_code == 422

    # Incorrect lengths
    incorrect_data = {
        "username": "lx",
        "password": "password",
        "email": "x@y"
    }

    response = client.post("/users/", json=incorrect_data)
    assert response.status_code == 422



