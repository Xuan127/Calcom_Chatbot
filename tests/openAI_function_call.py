import openai

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Use this API endpoint to retrieve all available bookable slots for a user \
                or team event type within a specified date and time range. \
                This can be particularly useful when you need to check availability for scheduling purposes. \
                For instance, call this API when a user wants to book an appointment or when you \
                need to display all possible time slots for an event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "eventTypeId": {
                        "type": "integer",
                        "description": "Event type's ID.",
                    },
                    "startTime": {
                        "type": "string",
                        "description": "Start time to search for availability.",
                    },
                    "endTime": {
                        "type": "string",
                        "description": "End time to search for availability.",
                    },
                    "timeZone": {
                        "type": "string",
                        "description": "Timezone to search for availability.",
                    },
                },
                "required": ["eventTypeId", "startTime", "endTime"],
                "additionalProperties": False,
            },
        }
    }
]

messages = [
    {"role": "system", "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user."},
    {"role": "user", "content": "Hi, can you help me see what available slots are there to be booked?"},
    {"role": "assistant", "content": "Sure, I can help with that. \n\nCould you please provide me with the following information:\n1. The event type's ID.\n2. The start time and end time for the period you're interested in.\n3. The timezone you're in (if relevant)."},
    {"role": "user", "content": "EventId is 1181131, start time will be the first day of 2024, end time will be the last day of 2024"}
]

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

print(response.choices[0].message)