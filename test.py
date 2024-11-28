# Import the necessary libraries
import pytest
from app import app  # Import the Flask app we want to test


# Set up a test client for Flask
@pytest.fixture
def client():
    # This creates a client that we can use to make requests to our app
    with app.test_client() as client:
        yield client


# Test the "Recommend Destination" intent
def test_recommend_destination(client):
    # Simulate a request from Dialogflow where the user gives a vacation preference
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "Recommend Destination"},
                "parameters": {"vacation_preference": "relaxation"},
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the response suggests the correct destinations
    assert b"For relaxation, I recommend visiting Maldives, Bora Bora." in response.data


# Test "City Details" with the city provided
def test_city_details_with_city(client):
    # Simulate a request for city details, specifying "Maldives"
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "City Details"},
                "parameters": {"city": "Maldives"},
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the details for "Maldives" are in the response
    assert b"In Maldives, you can enjoy crystal-clear beaches" in response.data


# Test "Visa Details" with the city provided
def test_visa_details_with_city(client):
    # Simulate a request for visa details with "Tokyo" specified
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "Visa Details"},
                "parameters": {"city": "Tokyo"},
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the visa details for "Tokyo" are in the response
    assert (
        b"U.S. citizens can travel visa-free for up to 90 days in Japan"
        in response.data
    )


# Test "Visa Details" without providing a city
def test_visa_details_without_city(client):
    # Simulate a request without specifying a city
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "Visa Details"},
                "parameters": {"city": ""},
                "outputContexts": [
                    {
                        "name": "projects/test-project/agent/sessions/test-session/contexts/destination-followup",
                        "parameters": {"city": "Paris"},
                    }
                ],
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the visa details for "Paris" are in the response
    assert (
        b"U.S. citizens can stay visa-free for up to 90 days within the Schengen Area"
        in response.data
    )


# Test "Cost Details" with the city provided
def test_cost_details_with_city(client):
    # Simulate a request for cost details with "Bora Bora" specified
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "Cost Details"},
                "parameters": {"city": "Bora Bora"},
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the cost details for "Bora Bora" are in the response
    assert b"A trip to Bora Bora generally costs $4000 to $8000" in response.data


# Test "Cost Details" without providing a city
def test_cost_details_without_city(client):
    # Simulate a request without specifying a city
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "Cost Details"},
                "parameters": {"city": ""},
                "outputContexts": [
                    {
                        "name": "projects/test-project/agent/sessions/test-session/contexts/destination-followup",
                        "parameters": {"city": "Banff"},
                    }
                ],
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the cost details for "Banff" are in the response
    assert b"Visiting Banff costs approximately $2000 to $4000" in response.data


# Test an unidentified intent
def test_unidentified_intent(client):
    # Simulate a request with an unrecognized intent
    response = client.post(
        "/webhook",
        json={
            "queryResult": {
                "intent": {"displayName": "Unknown Intent"},
                "parameters": {},
            },
            "session": "projects/test-project/agent/sessions/test-session",
        },
    )
    # Check if the response contains the fallback message
    assert (
        b"I'm sorry, I couldn't process that. Could you please reword your response?"
        in response.data
    )
