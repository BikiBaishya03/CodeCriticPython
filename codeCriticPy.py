import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

def load_standard_file():
    try:
        with open("standard.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error : standard.json file not present...")
        return {}

def extract_rule(language, standard_dict):
    
    "Fallback rule if language is not present in standard_dict"
    fallback_rule = "Analyze for general clean code principles and time/space complexity and focus on redability and industry standard."
    
    return standard_dict.get(language.lower(),fallback_rule)


def model_call(user_prompt,rule):
    System_prompt = """
    You are an interactive Ai assistant who is expert at analyzing code and advicing on how to improvement it and fix if there any mistake in the user code.
    
    ## Tone and style:
        - Your responses should be short and concise.
        - Only use emojis if the user explicitly requests it.
        - Use Github-flavored markdown for formatting. 
        - Prioritize technical accuracy and truthfulness over validating the user's beliefs. Focus on facts and problem-solving, providing direct, objective technical info without any unnecessary superlatives, praise, or emotional validation.
    
    ## Doing tasks

        -The user will primarily request software engineering tasks.
        -For these tasks the following steps are recommended:
            - Analyze the code throuly .
            - Decide what are the possible changes that can be doe to imporve the code.
            - update the code with fixes and add comment on why you choosed this.
            - return the updated code.
            
    #Important Rules:

        - Always return the response in strict json format.
        
    ## Output format : 
        {
            "rating": "number",
            "issues": list,
            "fix": "string"
        }


    
    ## Additional Context : """ + rule + """
    
        ## Example 1:
        input:"
            num1 = input("Enter first number: ")
            num2 = input("Enter second number: ")

            result = num1 + num2

            print("Sum =", result)
        " 
        output :{
                "rating": 8,
                "issues": [
                    "Using string input to add the numbers in line 3 without converting them to integer."
                ],
                "fix": "You should convert the values returned by input() to integers using int() before adding them. Otherwise, Python treats them as strings and joins them together instead of performing arithmetic addition."
            }
            
        ## Example 2:
        input_text = '''
                result = ""

                for i in range(1000):
                    result += str(i)

                print(result)
            '''
        output :{
                "rating": 7.5,
                "issues": [
                    "Using + to concatinate two string."
                ],
                "fix": "You should accumulate the strings in a list and use "".join() at the end instead of repeatedly concatenating with += inside the loop. String concatenation creates a new string object each time and can be inefficient for large loops."
            }
    """
    
    client = OpenAI(
        api_key=os.getenv("GEMINi_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role" : "system" , "content" : System_prompt},
            {"role" : "user" , "content" : user_prompt}
        ],
        response_format={"type":"json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


class CodeRequest(BaseModel):
    language : str
    code : str

app = FastAPI()
@app.post("/chat")
def chat(request : CodeRequest):
    standard_dict = load_standard_file()
    rule = extract_rule(request.language,standard_dict)
    response = model_call(request.code,rule)

    return response
