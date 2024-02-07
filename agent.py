from openai import AsyncOpenAI
import time
import asyncio
import json
from agent_tools import tools
class Agent:
    async def __init__(self, name, engine, agent_type):
        self.client = AsyncOpenAI()
        self.thread = None
        self.run = None
        self.name = name
        self.agent_type = agent_type
        self.agent = await self.client.beta.assistants.create(model=engine, name=self.name, tools=self.load_tools(f'tools/{self.agent_type}.json'), instructions=self.load_prompt(f'prompts/{self.agent_type}.txt'))

    def load_tools(self, file):
        with open(file, 'r') as f:
            return json.load(f)
    
    def load_prompt(self, file):
        with open(file, 'r') as f:
            return f.read()

    async def create_thread(self):
        self.thread = await self.client.beta.threads.create()

    async def create_run(self):
        self.run = await self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.agent.id)

    async def add_message(self, role, message):
        await self.client.beta.threads.messages.create(thread_id=self.thread.id, role=role, content=message)

    async def get_response(self):
        retrieved = await self.client.beta.threads.runs.retrieve(run_id=self.run.id, thread_id=self.thread.id)
        while not retrieved.done():
            asyncio.sleep(1)
            
        status = retrieved.model_dump()['status']
        print(f'{self.name} status: {status}')
        
        if status == 'completed':
            messages = await self.client.beta.threads.messages.list(
            thread_id=self.thread.id
            )
            return messages.model_dump()['data'][0]['content'][-1]['text']['value']


        elif status == 'requires_action':
            print(retrieved.model_dump())
            tool_list, run_id, thread_id = await self.run_function(retrieved.model_dump())
            #print(f'{name} tool list: {tool_list}')

            await self.client.beta.threads.runs.submit_tool_outputs(run_id=run_id, thread_id=thread_id, tool_outputs=tool_list)

        elif status == 'failed':
            print(retrieved.model_dump())
            print(f'{self.name} model failed to complete')
            return None


    async def run_function(retrieved):
        message = retrieved['required_action']['submit_tool_outputs']['tool_calls']
        tool_list = []
        run_id = retrieved['id']
        thread_id = retrieved['thread_id']
        for elem in message:
            print(elem['function']['name'])
            time.sleep(5)    
            tool_id = elem['id']
            arguments = json.loads(elem['function']['arguments'].replace(r"\n", "").replace(r"\t", "").replace(r"\'", ""))
                
            if elem['function']['name'] == 'prompt_user':
                response = tools['prompt_user'](prompt_to_user=arguments['prompt_to_user'])
                print(response)
            
            else:
                response = 'No response, invalid function'
                print(response)
                exit()
                
            tool_list.append({'tool_call_id': str(tool_id), 'output': str(response)})
            
        return tool_list, run_id, thread_id
        