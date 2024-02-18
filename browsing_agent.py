from agent import Agent
from selenium import webdriver
import time
import json
from agent_tools import tools
import base64
from openai import AsyncOpenAI
import asyncio
from mimetypes import guess_type
import pyautogui


class BrowsingAgent(Agent):
    def __init__(self, name, engine, agent_type, api_key):
        super().__init__(name, engine, agent_type, api_key)
        self.client = AsyncOpenAI(api_key=api_key)
        self.driver = webdriver.Chrome()
        self.message_list = []
        self.message_list.append({'role': 'system', 'content': self.load_prompt(f"prompts/{self.agent_type}.txt")})
        self.tools = self.load_tools(f"tools/{self.agent_type}.json")
        self.screenshot_prompt = self.load_prompt(f"prompts/screenshotter.txt")
        self.screenshot_system_prompt = self.load_prompt(f"prompts/screenshotter_system.txt")
        self.conversation = True

    
    async def load_page(self, url: str):
        self.driver.get(url)
        return f"Webpage loaded at {url}, continue to next step."

    async def view_page(self): 
        screenshot = self.driver.get_screenshot_as_png()

        screenshot = base64.b64encode(screenshot).decode('utf-8')
        
        #screenshot = str.encode(screenshot)
        screenshot = f"data:image/png;base64,{screenshot}"
        message = [
            {"role": "system", "content": self.screenshot_system_prompt},
            {"role": "user", "content": 
                [
                    {
                    "type": "image_url",
                    "image_url": screenshot
                    },
                    {
                        "type": "text",
                        "text": self.screenshot_prompt
                    }  
                ]
             },
        ]

        response = await self.client.chat.completions.create(
            model='gpt-4-vision-preview',
            messages=message,
            stream=False,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    
    async def move_cursor(self, x: int, y: int):
        pyautogui.moveRel(x, y, duration=1.2)
        return f"Cursor moved relative to the past position by {x} pixels in the x direction and {y} pixels in the y direction."

    async def get_ai_response(self):
        response_generator = await self.client.chat.completions.create(
        model=self.engine,
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
            if len(response_chunk.choices) != 0:
                deltas = response_chunk.choices[0].delta
                if deltas != None and deltas.tool_calls != None:
                    if deltas.tool_calls[0].function.name != None:
                        function_name = deltas.tool_calls[0].function.name
                    if deltas.tool_calls[0].function.arguments != None:    
                        function_arguments = deltas.tool_calls[0].function.arguments
                    #print(function_name)
                    #print(function_arguments)
                    if function_arguments != '' or None:
                        tool_args.append(function_arguments)#.replace('"', '').replace("'", ''))
                    if len(tool_args)>0 and "}" in tool_args[-1]:
                        tool_args = ''.join(tool_args)
                        tool_args = json.loads(tool_args)
                        tool_dict = {}
                        tool_dict[function_name] = tool_args

                    
                        print(f"function name: {function_name}, function args: {tool_args}")
                        #print(tool_dict)
                        function_response = await self.call_function(
                            tool_dict
                        )
                        tool_dict = {}
                        tool_args = []
                        function_flag = True
                if deltas.content != None:
                    yield deltas.content, function_flag, function_response

        yield deltas.content, function_flag, function_response                      

    async def end_conversation(self):
        return False

    async def call_function(self, func_call):
        for function_name, function_args in func_call.items():
            if function_name == 'view_page':
                response = await self.view_page(**function_args)
                
            elif function_name == 'move_cursor':
                response = await self.move_cursor(**function_args)
                
            elif function_name == 'load_page':
                print("load function")
                response = await self.load_page(**function_args)
                
            elif function_name == 'end_conversation':
                response = await self.end_conversation(**function_args)
                #func_output[function_name] = response
                self.conversation = False

        return response
       
    async def create_run(self, message):
        text_storage = ""
        self.message_list.append({'role': 'user', 'content': message})
        while True:
            text_storage = ''
            await_response = False
            initial_response = True
            #print(chat_history)
            async for text, function_flag, function_responses in self.get_ai_response():
                #print(chat_history)
                print(text)
                if text != None:
                    if initial_response:
                        initial_response = False
                    text_storage = text_storage + text
                if function_flag:
                    text_storage = text_storage + "These are the tool call results: " + str(function_responses)
                    await_response = True
        
            self.message_list.append({'role': 'assistant', 'content': text_storage})
            

            
        
    def retrieve_messages(self):
        return self.message_list
    
