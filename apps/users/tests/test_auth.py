import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from common.tests.factories import CustomUserFactory
from common.tests.fixtures import create_groups,customer


@pytest.fixture
def api_client():
    return APIClient()


#=====================================================
# TA.1 USERBASE TESTS
@pytest.mark.django_db
class TestAuthApi:
    #T1 REGISTRAION
    def test_register_customer(self, api_client,create_groups):
        data = {
            "email": "newcust@example.com",
            "username": "newcust",
            "password": "pass12345",
            "password_confirm": "pass12345",
            "first_name": "New",
            "last_name": "Cust",
            "phone_number": "+919911112222",
            "utype": "c",
        }
        res = api_client.post("/api/v1/auth/register/", data, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        assert "access" in res.data
        assert "refresh" in res.data

    #T2 PASSWORD MISMATCH
    def test_register_password_mismatch(self, api_client):
        data = {
            "email": "x@example.com",
            "username": "x1",
            "password": "pass12345",
            "password_confirm": "wrong12345",
            "first_name": "A",
            "last_name": "B",
            "phone_number": "+919933334444",
            "utype": "c",
        }
        res = api_client.post("/api/v1/auth/register/", data, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    #T3 LOGIN SUCCESSFULL
    def test_login_success(self, api_client):
        user = CustomUserFactory(email="login@example.com", username="loginuser", utype="c")
        user.set_password("pass12345")
        user.save(update_fields=["password"])

        res = api_client.post("/api/v1/auth/login/", {
            "email": "login@example.com",
            "password": "pass12345",
        }, format="json")

        assert res.status_code == status.HTTP_200_OK
        assert "access" in res.data

    #T4 LOGOUT TEST
    def test_logout_success(self, api_client, customer):
        refresh = RefreshToken.for_user(customer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")

        res = api_client.post("/api/v1/auth/logout/", {"refresh_token": str(refresh)}, format="json")
        assert res.status_code == status.HTTP_205_RESET_CONTENT

    #T5 DUPLICATE EMAIL
    def test_registration_duplicate_email(self,api_client,customer):
        print("=====test3 duplicate email=====")
        data = {
            'email':'testcust@test.com', #already exists
            'username':'anothercust',
            'password':'strongpass123',
            'password_confirm':'strongpass123',
            'first_name':'Another',
            'last_name':'Customer',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/v1/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        assert response.status_code == 400
