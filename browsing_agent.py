from agent import Agent
from selenium import webdriver
import time
import json
from agent_tools import tools
import base64
from openai import AsyncOpenAI
import asyncio
from mimetypes import guess_type

class BrowsingAgent(Agent):
    def __init__(self, name, engine, agent_type, api_key):
        super().__init__(name, engine, agent_type, api_key)
        self.client = AsyncOpenAI(api_key=api_key)
        self.driver = webdriver.Chrome()
        self.message_list = []
        self.message_list.append({'role': 'system', 'content': self.load_prompt(f"prompts/{self.agent_type}.txt")})
        self.tools = self.load_tools(f"tools/{self.agent_type}.json")
        self.screenshot_prompt = self.load_prompt(f"prompts/screenshotter.txt")
    
    async def view_page(self, url: str):
        self.driver.get(url)
        #time.sleep(1)
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = base64.b64encode(screenshot).decode('utf-8')
        
        #screenshot = str.encode(screenshot)
        screenshot = f"data:image/png;base64,{screenshot}"
        message = [
            {"role": "system", "content": self.screenshot_prompt},
            {"role": "user", "content": 
                [
                    {
                        "type": "text",
                        "text": "I have provided a screenshot of the current webpage. Reply with a complete description of the webpage. For context, your description of the page will be used by other models to browse the page, so a complete verbose description is required."
                    },
                    {
                    "type": "image_url",
                    "image_url": screenshot
                    }    
                ]
             },
        ]

        response = await self.client.chat.completions.create(
            model='gpt-4-vision-preview',
            messages=message,
            stream=False,
            max_tokens=2048,
        )
        return response.choices[0].message.content
        
    async def get_ai_response(self):
        response_generator = await self.client.chat.completions.create(
            model='gpt-4-vision-preview',
            messages=self.message_list,
            stream=True,
            tools=self.tools,
            tool_choice='auto'
        )
        func_call = {}
        tool_args = []
        function_response = {}
        function_flag = False

        async for response_chunk in response_generator:
            if response_chunk.choices != None:
                deltas = response_chunk.choices[0].delta
                if deltas != None and deltas.tool_calls != None:
                    if deltas.tool_calls[0].function.name != None:
                        function_name = deltas.tool_calls[0].function.name
                    if deltas.tool_calls[0].function.arguments != None:    
                        function_arguments = deltas.tool_calls[0].function.arguments
                    if function_arguments != '' or None:
                        tool_args.append(function_arguments.replace('"', '').replace("'", ''))
                    if len(tool_args)>0 and "}" in tool_args[-1]:
                        tool_args = ''.join(tool_args)
                        tool_dict = {}
                        x = tool_args.split(':')
                        first = x[0].replace('{', '').replace('}', '').replace(' ', '')
                        second = x[1].replace('{', '').replace('}', '').replace(' ', '')
                        tool_dict[first] = second
                        func_call[function_name] = tool_dict
                        function_response[function_name] = self.call_function(
                            func_call
                        )
                        tool_dict = {}
                        func_call = {}
                        tool_args = []
                        function_flag = True
                if deltas.content != None:
                    yield deltas.content, function_flag, function_response

        yield deltas.content, function_flag, function_response                


    def call_function(self, func_call):
        func_output = {}
        for function_name, function_args in func_call.items():
            if function_name == 'take_screenshot':
                response = self.take_screenshot(**function_args)
                func_output[function_name] = response
        return func_output
       
    async def create_run(self, message):
        text_storage = ""
        self.message_list.append({'role': 'user', 'content': message})
        await_response = True
        while await_response == True:
            async for text, function_flag, function_responses in self.get_ai_response():
                if text != None:
                    text_storage = text_storage + text
                    await_response = False
                if function_flag:
                    text_storage = text_storage + "Incorporate the results of the function calling into your context. These are the function call results: " + str(function_responses)
                    await_response = True
        
        self.message_list.append({'role': 'assistant', 'content': text_storage})

    def retrieve_messages(self):
        return self.message_list
    
