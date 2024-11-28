# Import necessary modules from Flask
from flask import Flask, request, jsonify, render_template

# Create an instance of the Flask application
app = Flask(__name__)

# Dictionary containing city data for different vacation preferences
# Each city has information about vacation type, visa details, city highlights, and cost
city_data = {
    "Maldives": {
        "vacation_preference": "relaxation",
        "visa_details": "For Maldives, U.S. citizens generally don’t need a visa for stays up to 30 days.",
        "city_details": "In Maldives, you can enjoy crystal-clear beaches, luxurious overwater bungalows, and vibrant coral reefs.",
        "cost_details": "The cost of visiting Maldives typically ranges from $3000 to $7000, depending on your preferences.",
    },
    "Bora Bora": {
        "vacation_preference": "relaxation",
        "visa_details": "For Bora Bora (French Polynesia), U.S. citizens can stay visa-free for up to 90 days.",
        "city_details": "Bora Bora is famous for its turquoise lagoons, luxury resorts, and romantic sunsets.",
        "cost_details": "A trip to Bora Bora generally costs $4000 to $8000.",
    },
    "Queenstown": {
        "vacation_preference": "adventure",
        "visa_details": "For New Zealand, U.S. citizens can travel visa-free for up to 90 days.",
        "city_details": "Queenstown offers thrilling adventures, from bungee jumping to exploring stunning fjords in Milford Sound.",
        "cost_details": "A trip to Queenstown typically costs around $2500 to $6000, depending on activities.",
    },
    "Banff": {
        "vacation_preference": "adventure",
        "visa_details": "For Canada, U.S. citizens do not require a visa for stays under 6 months.",
        "city_details": "Banff boasts breathtaking mountain scenery, world-class skiing, and stunning glacier-fed lakes.",
        "cost_details": "Visiting Banff costs approximately $2000 to $4000, depending on your itinerary.",
    },
    "Tokyo": {
        "vacation_preference": "city exploration",
        "visa_details": "For Tokyo, U.S. citizens can travel visa-free for up to 90 days in Japan.",
        "city_details": "Tokyo is a bustling city filled with vibrant neighborhoods, ancient temples, and incredible street food.",
        "cost_details": "Visiting Tokyo typically costs $2000 to $5000, depending on activities, food, and accommodation preferences.",
    },
    "Paris": {
        "vacation_preference": "city exploration",
        "visa_details": "For France, U.S. citizens can stay visa-free for up to 90 days within the Schengen Area.",
        "city_details": "Paris offers iconic landmarks like the Eiffel Tower, world-class art museums, and charming cafes.",
        "cost_details": "A trip to Paris usually costs $2500 to $5500, including food, activities, and accommodations.",
    },
}


# Define the root route to serve the homepage
@app.route("/")
def index():
    # Render the 'index.html' template located in the 'templates' folder
    return render_template("index.html")


# Define a webhook endpoint to handle requests from Dialogflow
@app.route("/webhook", methods=["POST"])
def webhook():
    # Parse the JSON request sent by Dialogflow
    req = request.get_json()

    # Extract the intent name (e.g., "Recommend Destination") from the request
    intent_name = req["queryResult"]["intent"]["displayName"]

    # Extract user-provided parameters (e.g., vacation preference, city)
    parameters = req["queryResult"]["parameters"]
    vacation_preference = parameters.get("vacation_preference", None)  # Vacation type
    city_name = parameters.get("city", None)  # City name

    # Retrieve project_id and session_id from the request's session path
    session_path = req[
        "session"
    ]  # Format: projects/{project_id}/agent/sessions/{session_id}
    project_id = session_path.split("/")[1]  # Extract project_id
    session_id = session_path.split("/")[-1]  # Extract session_id

    # Handle "Recommend Destination" intent
    if intent_name == "Recommend Destination":
        # If no vacation preference is provided, ask the user for one
        if not vacation_preference:
            return jsonify(
                {
                    "fulfillmentText": "Do you prefer relaxation, adventure, or city exploration?"
                }
            )

        # Find cities that match the user's vacation preference
        recommended_cities = [
            city
            for city, details in city_data.items()
            if details["vacation_preference"] == vacation_preference
        ]

        # If no cities match, ask the user to try again
        if not recommended_cities:
            return jsonify(
                {
                    "fulfillmentText": f"Sorry, I couldn't find cities for {vacation_preference}. Please choose a different vacation preference."
                }
            )

        # Respond with a list of recommended cities and save the vacation preference in the context
        return jsonify(
            {
                "fulfillmentText": f"For {vacation_preference}, I recommend visiting {', '.join(recommended_cities)}. Which one would you like to know more about?",
                "outputContexts": [
                    {
                        "name": f"projects/{project_id}/agent/sessions/{session_id}/contexts/destination-followup",
                        "lifespanCount": 5,  # Context lasts for 5 interactions
                        "parameters": {
                            "vacation_preference": vacation_preference,
                        },
                    }
                ],
            }
        )

    # Handle "City Details" intent
    elif intent_name == "City Details":
        # If city is not provided, try to retrieve it from the context
        if not city_name:
            input_contexts = req["queryResult"].get("outputContexts", [])
            for context in input_contexts:
                if "destination-followup" in context["name"]:
                    city_name = context["parameters"].get("city", None)
                    break

        # If the city is valid, provide details and save it in the context
        if city_name and city_name in city_data:
            return jsonify(
                {
                    "fulfillmentText": city_data[city_name]["city_details"],
                    "outputContexts": [
                        {
                            "name": f"projects/{project_id}/agent/sessions/{session_id}/contexts/destination-followup",
                            "lifespanCount": 5,
                            "parameters": {"city": city_name},
                        }
                    ],
                }
            )

        # If city is invalid, ask for clarification
        return jsonify(
            {
                "fulfillmentText": "Sorry, I couldn't find details for that city. Please provide a valid city."
            }
        )

    # Handle "Visa Details" intent
    elif intent_name == "Visa Details":
        # If city is not provided, try to retrieve it from the context
        if not city_name:
            input_contexts = req["queryResult"].get("outputContexts", [])
            for context in input_contexts:
                if "destination-followup" in context["name"]:
                    city_name = context["parameters"].get("city", None)
                    break

        # If the city is valid, provide visa details
        if city_name and city_name in city_data:
            return jsonify({"fulfillmentText": city_data[city_name]["visa_details"]})

        # If city is invalid, ask for clarification
        return jsonify(
            {
                "fulfillmentText": "Sorry, I couldn't find visa details for that city. Can you provide the city name?"
            }
        )

    # Handle "Cost Details" intent
    elif intent_name == "Cost Details":
        # If city is not provided, try to retrieve it from the context
        if not city_name:
            input_contexts = req["queryResult"].get("outputContexts", [])
            for context in input_contexts:
                if "destination-followup" in context["name"]:
                    city_name = context["parameters"].get("city", None)
                    break

        # If the city is valid, provide cost details
        if city_name and city_name in city_data:
            return jsonify({"fulfillmentText": city_data[city_name]["cost_details"]})

        # If city is invalid, ask for clarification
        return jsonify(
            {
                "fulfillmentText": "Sorry, I couldn't find cost details for that city. Can you provide the city name?"
            }
        )

    # Handle unrecognized intents
    else:
        return jsonify(
            {
                "fulfillmentText": "I'm sorry, I couldn't process that. Could you please reword your response?"
            }
        )


# Run the Flask application on the specified port
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
