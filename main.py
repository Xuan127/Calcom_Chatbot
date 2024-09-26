import openai
from openai import OpenAI
import streamlit as st
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
from enum import Enum
import requests

calcom_api_key = "cal_live_767d038da060f887e1d230a9031e6412"

# Calling APIs with arguments returned by the assistant
def call_get_slots(arguments):
    api_url = "https://api.cal.com/v1/slots?apiKey=" + calcom_api_key
    if arguments.eventTypeId: api_url += '&eventTypeId=' + str(arguments.eventTypeId)
    api_url += '&startTime=' + arguments.startTime
    api_url += '&endTime=' + arguments.endTime
    if arguments.timeZone: api_url += '&timeZone=' + arguments.timeZone
    # usernameList not implemented
    if arguments.eventTypeSlug: api_url += '&eventTypeSlug=' + arguments.eventTypeSlug
    if arguments.orgSlug: api_url += '&orgSlug=' + arguments.orgSlug
    if arguments.isTeamEvent: api_url += '&isTeamEvent=' + str(arguments.isTeamEvent)

    payload = {}
    headers = {}

    # Send the GET request
    response = requests.get(api_url, headers=headers, json=payload)
    return response

def call_find_all_bookings(arguments):
    api_url = "https://api.cal.com/v1/bookings?apiKey=" + calcom_api_key
    if arguments.userId: api_url += '&userId=' + str(arguments.userId)
    if arguments.take: api_url += '&take=' + str(arguments.take)
    if arguments.page: api_url += '&page=' + str(arguments.page)
    if arguments.attendeeEmail: api_url += '&attendeeEmail=' + arguments.attendeeEmail

    payload = {}
    headers = {}

    # Send the GET request
    response = requests.get(api_url, headers=headers, json=payload)
    return response

def call_find_a_booking(arguments):
    api_url = f"https://api.cal.com/v1/bookings/{arguments.id}?apiKey=" + calcom_api_key

    payload = {}
    headers = {}

    # Send the GET request
    response = requests.get(api_url, headers=headers, json=payload)
    return response

def call_create_new_booking(arguments):
    api_url = "https://api.cal.com/v1/bookings?apiKey=" + calcom_api_key

    payload = {
        "eventTypeId": arguments.eventTypeId,
        "start": arguments.start,
        "responses": {
            "name": arguments.responses_name,
            "email": arguments.responses_email,
            "guests": [],
            "location": {
                "value": arguments.responses_location,
                "optionValue": ""
            }
        },
        "metadata": {},
        "timeZone": arguments.timeZone,
        "language": arguments.language
    }
    if arguments.end: payload.setdefault('end', arguments.end)
    if arguments.title: payload.setdefault('title', arguments.title)
    if arguments.recurringEventId: payload.setdefault('recurringEventId', arguments.recurringEventId)
    if arguments.description: payload.setdefault('description', arguments.description)
    if arguments.status: payload.setdefault('status', arguments.status)
    if arguments.seatsPerTimeSlot: payload.setdefault('seatsPerTimeSlot', arguments.seatsPerTimeSlot)
    if arguments.seatsShowAttendees: payload.setdefault('seatsShowAttendees', arguments.seatsShowAttendees)
    if arguments.seatsShowAvailabilityCount: payload.setdefault('seatsShowAvailabilityCount', arguments.seatsShowAvailabilityCount)
    headers = {}

    # Send the POST request
    response = requests.post(api_url, headers=headers, json=payload)
    return response

def call_edit_booking(arguments):
    api_url = f"https://api.cal.com/v1/bookings/{arguments.id}?apiKey=" + calcom_api_key

    payload = {}
    if arguments.title: payload.setdefault('title', arguments.title)
    if arguments.startTime: payload.setdefault('startTime', arguments.startTime)
    if arguments.endTime: payload.setdefault('endTime', arguments.endTime)
    if arguments.status: payload.setdefault('status', arguments.status)
    if arguments.description: payload.setdefault('description', arguments.description)
    headers = {}

    # Send the PATCH request
    response = requests.patch(api_url, headers=headers, json=payload)
    return response

def call_cancel_booking(arguments):
    api_url = f"https://api.cal.com/v1/bookings/{arguments.id}/cancel?apiKey=" + calcom_api_key
    if arguments.allRemainingBookings: api_url += '&allRemainingBookings=' + str(arguments.allRemainingBookings)
    if arguments.cancellationReason: api_url += '&cancellationReason=' + str(arguments.cancellationReason)

    payload = {}
    headers = {}

    # Send the DELETE request
    response = requests.delete(api_url, headers=headers, json=payload)
    return response

def api_response_to_agent(response):
    # Check and print the response
    if response.status_code == 200:
        st.session_state.messages.append({
            "role": "system", 
            "content": "The API call was successful, here is the response, \
                present it to the user in a easy to understand way" + json.dumps(response.json())
        })
    else:
        st.session_state.messages.append({
            "role": "system", 
            "content": "The API call was unsuccessful, here is the error code and message, \
                present it to the user in a easy to understand way" 
                + str(response.status_code) + response.text
        })
    completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto"
    )
    response = completion.choices[0].message
    st.session_state.messages.append({"role": "assistant", "content": response.content})
    st.chat_message("assistant").write(response.content)

# Setting the formats of the arguments that the assistant should return
class BookingStatus(str, Enum):
    CANCELLED = "CANCELLED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"
    AWAITING_HOST = "AWAITING_HOST"

class Get_available_slots(BaseModel):
    eventTypeId: Optional[int]
    startTime: str
    endTime: str
    timeZone: Optional[str]
    usernameList: Optional[list[str]]
    eventTypeSlug: Optional[str]
    orgSlug: Optional[str]
    isTeamEvent: Optional[bool]

class Find_all_existing_bookings(BaseModel):
    userId: Optional[int]
    take: Optional[int]
    page: Optional[int]
    attendeeEmail: Optional[str]

class Find_a_existing_booking(BaseModel):
    id: int

class Create_new_booking(BaseModel):
    eventTypeId: int
    start: str
    end: Optional[str]
    responses_name: str
    responses_email: str
    responses_location: str
    timeZone: str
    language: str
    title: Optional[str]
    recurringEventId: Optional[int]
    description: Optional[str]
    status: Optional[BookingStatus]
    seatsPerTimeSlot: Optional[int]
    seatsShowAttendees: Optional[bool]
    seatsShowAvailabilityCount: Optional[bool]

class Edit_existing_booking(BaseModel):
    id: int
    title: Optional[int]
    startTime: Optional[str]
    endTime: Optional[str]
    status: Optional[BookingStatus]
    description: Optional[str]

class Cancel_existing_booking(BaseModel):
    allRemainingBookings: Optional[bool]
    cancellationReason: Optional[int]
    id: int

# tools to be passed into the module
tools = []
tools.append(openai.pydantic_function_tool(Get_available_slots))
tools.append(openai.pydantic_function_tool(Find_all_existing_bookings))
tools.append(openai.pydantic_function_tool(Find_a_existing_booking))
tools.append(openai.pydantic_function_tool(Create_new_booking))
tools.append(openai.pydantic_function_tool(Edit_existing_booking))
tools.append(openai.pydantic_function_tool(Cancel_existing_booking))

# include descriptions in the tools
get_slots_description = Path('get_slots_description.txt').read_text(encoding='utf-8')
tools[0]['function']['description'] = get_slots_description
tools[0]['function']['parameters']['properties']['eventTypeId']['description'] = "The ID of the event type associated with the booking, this is optional"
tools[0]['function']['parameters']['properties']['startTime']['description'] = "Start time to search for availability, example format: 2012-04-23T18:25:43.511Z"
tools[0]['function']['parameters']['properties']['endTime']['description'] = "End time to search for availability, example format: 2012-04-23T18:25:43.511Z"
tools[0]['function']['parameters']['properties']['timeZone']['description'] = "Timezone to search for availability, this is optional, example: Asia/Singapore"

get_all_bookings_description = Path('get_all_bookings_description.txt').read_text(encoding='utf-8')
tools[1]['function']['description'] = get_all_bookings_description
tools[1]['function']['parameters']['properties']['userId']['description'] = "The ID of the user associated with the booking, this is optional"

get_a_booking_description = Path('get_a_booking_description.txt').read_text(encoding='utf-8')
tools[2]['function']['description'] = get_a_booking_description
tools[2]['function']['parameters']['properties']['id']['description'] = "ID of the specific booking that the user is looking for"

create_booking_description = Path('create_booking_description.txt').read_text(encoding='utf-8')
tools[3]['function']['description'] = create_booking_description
tools[3]['function']['parameters']['properties']['eventTypeId']['description'] = "The ID of the event type associated with the booking"
tools[3]['function']['parameters']['properties']['start']['description'] = "The start time of the booking, example format: 2012-04-23T18:25:43.511Z"
tools[3]['function']['parameters']['properties']['end']['description'] = "The end time of the booking, example format: 2012-04-23T18:25:43.511Z, this is optional"
tools[3]['function']['parameters']['properties']['responses_name']['description'] = "Participant of the meeting"
tools[3]['function']['parameters']['properties']['responses_email']['description'] = "email of the participant of the meeting"
tools[3]['function']['parameters']['properties']['responses_location']['description'] = "location of the meeting"
tools[3]['function']['parameters']['properties']['timeZone']['description'] = "Timezone to search for availability, example: Asia/Singapore"
tools[3]['function']['parameters']['properties']['language']['description'] = "language of the booking, example: en"
tools[3]['function']['parameters']['properties']['title']['description'] = "The title of the booking, this is optional"
tools[3]['function']['parameters']['properties']['description']['description'] = "The description of the booking, this is optional"
tools[3]['function']['parameters']['properties']['status']['description'] = "The current status of the booking, this is optional"

edit_booking_description = Path('edit_booking_description.txt').read_text(encoding='utf-8')
tools[4]['function']['description'] = edit_booking_description
tools[4]['function']['parameters']['properties']['id']['description'] = "ID of the specific booking that the user is looking for"

cancel_booking_description = Path('cancel_booking_description.txt').read_text(encoding='utf-8')
tools[5]['function']['description'] = cancel_booking_description
tools[5]['function']['parameters']['properties']['id']['description'] = "ID of the specific booking that the user is looking for"

# json_formatted_str = json.dumps(tools, indent=2)
# print(json_formatted_str)

st.title("💬 Cal.com Assistant Chatbot")

if "messages" not in st.session_state:
    system_prompt = Path('system_prompt.txt').read_text(encoding='utf-8')
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["messages"] = [{"role": "assistant", "content": "I am your Cal.com Assistant! \
        I can help with you listing, creating, editing and cancelling bookings. \
        Let me know what I can do for you!"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    we_did_not_specify_stop_tokens = True
    try:
        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto"
        )
        print(completion)
        print()
        finish_reason = completion.choices[0].finish_reason
        response = completion.choices[0].message
        # Check if the conversation was too long for the context window, resulting in incomplete JSON 
        if finish_reason == "length":
            # your code should handle this error case
            pass
        # Check if the model's output included restricted content, so the generation of JSON was halted and may be partial
        elif finish_reason == "content_filter":
            # your code should handle this error case
            pass
        elif finish_reason == 'tool_calls':
            func_to_call = response.tool_calls[0].function.name
            if func_to_call == 'Get_available_slots':
                r = call_get_slots(response.tool_calls[0].function.parsed_arguments)
            if func_to_call == 'Find_all_existing_bookings':
                r = call_find_all_bookings(response.tool_calls[0].function.parsed_arguments)
            if func_to_call == 'Find_a_existing_booking':
                r = call_find_a_booking(response.tool_calls[0].function.parsed_arguments)
            if func_to_call == 'Create_new_booking':
                r = call_create_new_booking(response.tool_calls[0].function.parsed_arguments)
            if func_to_call == 'Edit_existing_booking':
                r = call_edit_booking(response.tool_calls[0].function.parsed_arguments)
            if func_to_call == 'Cancel_existing_booking':
                r = call_cancel_booking(response.tool_calls[0].function.parsed_arguments)
            api_response_to_agent(r)
        elif finish_reason == "stop":
            # In this case the model has either successfully finished generating the JSON object according to your schema, 
            # or the model generated one of the tokens you provided as a "stop token"
            if we_did_not_specify_stop_tokens:
                if response.refusal:
                    # handle refusal
                    st.session_state.messages.append({"role": "assistant", "content": response.refusal})
                    st.chat_message("assistant").write(response.refusal)
                else:
                    st.session_state.messages.append({"role": "assistant", "content": response.content})
                    st.chat_message("assistant").write(response.content)
            else:
                # Check if the response.choices[0].message.content ends with one of your stop tokens and handle appropriately
                pass
    except Exception as e:
        # Handle edge cases
        if type(e) == openai.LengthFinishReasonError:
            # Retry with a higher max tokens
            print("Too many tokens: ", e)
            pass
        else:
            # Handle other exceptions
            print(e)
            pass