import openai
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
import requests

calcom_api_key = "cal_live_767d038da060f887e1d230a9031e6412"

client = OpenAI()

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

    # Check and print the response
    if response.status_code == 200:
        return False, response.json()
    else:
        return True, (response.status_code, response.text)

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

we_did_not_specify_stop_tokens = True
try:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Hi, can you help me see what available slots are there to be booked? EventId is 1181131, start time will be the first day of 2024, end time will be the last day of 2024, I am in Singapore"},
        ],
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
            call_get_slots(response.tool_calls[0].function.parsed_arguments)
        else:
            pass
    elif finish_reason == "stop":
        # In this case the model has either successfully finished generating the JSON object according to your schema, 
        # or the model generated one of the tokens you provided as a "stop token"
        if we_did_not_specify_stop_tokens:
            if response.refusal:
                # handle refusal
                print(response.refusal)
            else:
                print(response.content)
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