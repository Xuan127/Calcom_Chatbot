import openai
from openai import OpenAI
import streamlit as st
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
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

    # Send the POST request
    response = requests.get(api_url, headers=headers, json=payload)
    return response

def call_find_all_bookings(arguments):
    pass

def call_create_new_booking(arguments):
    pass

def call_find_a_booking(arguments):
    pass

def call_edit_booking(arguments):
    pass

def call_cancel_booking(arguments):
    pass

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
    pass

class Create_new_booking(BaseModel):
    pass

class Find_a_existing_booking(BaseModel):
    pass

class Edit_existing_booking(BaseModel):
    pass

class Cancel_existing_booking(BaseModel):
    pass

# Reading txt files and saving as strings
get_slots_description = Path('get_slots_description.txt').read_text(encoding='utf-8')
system_prompt = Path('system_prompt.txt').read_text(encoding='utf-8')

# tools to be passed into the module
tools = []
tools.append(openai.pydantic_function_tool(Get_available_slots))
# include descriptions for getting slots
tools[0]['function']['description'] = get_slots_description
tools[0]['function']['parameters']['properties']['eventTypeId']['description'] = "Event type's ID. Each type of bookings has a unique ID, this is optional"
tools[0]['function']['parameters']['properties']['startTime']['description'] = "Start time to search for availability, example format: 2012-04-23T18:25:43.511Z"
tools[0]['function']['parameters']['properties']['endTime']['description'] = "End time to search for availability, example format: 2012-04-23T18:25:43.511Z"
tools[0]['function']['parameters']['properties']['timeZone']['description'] = "Timezone to search for availability, this is optional, example: Asia/Singapore"

# json_formatted_str = json.dumps(tools, indent=2)
# print(json_formatted_str)

st.title("💬 Cal.com Assistant Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

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