import os
import requests
import json
import platform
from dotenv import load_dotenv
import time
import subprocess

from google import genai
from google.genai import types

from langfuse import observe
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

load_dotenv()

current_platform = platform.system()

GoogleGenAIInstrumentor().instrument()

client = genai.Client()

@observe()
def run_command(command : str):
    result=subprocess.getoutput(command)
    return str(result)

@observe()
def get_weather(city : str):
    print("🛠️Tool called : get weather " ,city)
    url=f"https://wttr.in/{city}?format=%C+%t"
    response=requests.get(url)
    if response.status_code == 200:
        return f"The wheather of {city} is {response.text}."
    return "Something went wrong."

available_tools = {
    "run_command":{
        "fn":run_command,
        "description":"Takes a command as input and execute on system and return output"
    },
    "get_weather":{
        "fn":get_weather,
        "description":"This function take city name as input and return current weather of that city"
    }
}

system_prompt = """
    You are an helpful ai agent who is spcialized at resolving user query.
    You work on start , plan , action and observe mode.
    For the given user query and available tools, plan the step by step execution.
    Based on the planning, select the relevant tools from the available tools, and perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call, resolve the user query.

    CRITICAL CONTEXT:
    - You are executing commands on a system running: {current_os}
    - Tailor all commands passed to 'run_command' specifically for this operating system. 
      For example, if the OS is Windows, do not use Unix commands like 'touch', 'ls', or 'cat'. Instead, use 'type nul >', 'dir', or 'type'.
    - When running 'git commit' on Windows, you MUST enclose the commit message in double quotes (e.g., git commit -m "Your message here"). Never leave a commit message unquoted.
    - When checking if a file exists on Windows, ALWAYS use 'dir /b' instead of just 'dir' to avoid confusing terminal noise.
     
    Rules:
    -Follow the Output JSON format strctly
    - OUTPUT EXACTLY ONE JSON OBJECT PER TURN. NEVER output a JSON list or array ([]).
    -Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON format:
    {
        "step":"string,
        "content":"string",
        "function":"The name of the function if the step is action",
        "input":"The input parameter for the function"
    }

    Available tools:
    - run_command: Takes a command as input and execute on system and return output
    - get_weather: This function take city name as input and return current weather of that city

    Example:
    User Query : What is the wheather of New York?
    output: {"step":"plan", "content":"The user is interested in weather data in new york"}
    output: {"step":"plan", "content":"From the available tool i should call get_user"}
    output: {"step":"action", "function":"get_weather", "input":"new york"}
    output: {"step":"observe", "output":"12 Degree Celcius"}
    output: {"step":"output", "content":"The weather for new york seems to be 12 Degree Celcius"}
"""

messages = []

while True:
    user_query = input(">")
    if(user_query.lower() in ['exit','quit']):
        break
    
    messages.append({"role":"user" , "parts":[{"text":user_query}]})
    
    while True:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json"
            )
        )
        
        try:
            # Try to parse the JSON normally
            parsed_response = json.loads(response.text)
        except json.JSONDecodeError as e:
            # If the AI breaks the JSON rules, catch the error, print what it actually said, and skip the turn
            print(f"⚠️ AI returned invalid JSON. Raw output was:\n{response.text}")
            
            # Send an error message back to the AI so it knows it messed up and can try again
            error_json = json.dumps({ "step": "observe", "output": "System Error: You returned invalid JSON. You must return EXACTLY ONE valid JSON object per turn. Do not return multiple objects." })
            messages.append({"role": "user", "parts": [{"text": error_json}]})
            continue
        
        messages.append({"role":"model" , "parts":[{"text" :response.text}]})
        
        step = parsed_response.get("step")
       
        if step == "plan":
            print(f"🧠:{parsed_response.get('content')}")
            continue
        
        if step == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")
            
            if available_tools.get(tool_name):
                try:
                    if isinstance(tool_input,dict):
                        output = available_tools[tool_name]["fn"](**tool_input)
                    elif isinstance(tool_input,list):
                        output = available_tools[tool_name]["fn"](*tool_input) 
                    else:
                        output = available_tools[tool_name]["fn"](tool_input)
                except Exception as e:
                     output = f"Error : {str(e)}"

                observation_json = json.dumps({"step":"observer" , "output": str(output)})
                messages.append({"role":"user", "parts":[{"text":observation_json}]})
                continue
            else:
                error_json = json.dumps({"step":"observer" , "output": f"Tool {tool_name} does not exist"})
                messages.append({"role":"user", "parts":[{"text":error_json}]})
                continue
            
        if step == "output":
            print(f"🤖 : {parsed_response.get('content')}")
            break
        
        #time.sleep(3)
        
            
        
        
        
        
        
        

