import pytest
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from config.asgi import application
from common.tests.factories import CustomUserFactory


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_customer_ws_connect_and_echo():
    user = CustomUserFactory(utype="c")
    token = RefreshToken.for_user(user).access_token

    communicator = WebsocketCommunicator(
        application,
        f"/ws/customer/{user.id}/",
        headers=[(b"authorization", f"Bearer {str(token)}".encode("utf-8"))],
    )

    connected, _ = await communicator.connect()
    assert connected is True

    await communicator.send_json_to({"message": "hello"})
    response = await communicator.receive_json_from()
    assert response["message"] == "hello"

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_customer_ws_reject_other_user_room():
    user = CustomUserFactory(utype="c")
    other = CustomUserFactory(utype="c")
    token = RefreshToken.for_user(user).access_token

    communicator = WebsocketCommunicator(
        application,
        f"/ws/customer/{other.id}/",
        headers=[(b"authorization", f"Bearer {str(token)}".encode("utf-8"))],
    )

    connected, _ = await communicator.connect()
    assert connected is False
