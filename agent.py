from openai import OpenAI
import time
import asyncio
import json
from agent_tools import tools

class Agent:
    def __init__(self, name, engine, agent_type, api_key):
        self.client = OpenAI(api_key=api_key)
        self.thread = None
        self.run = None
        self.name = name
        self.agent_type = agent_type
        self.engine = engine
        self.file_dict = {}
    
    def create_agent(self):
        self.agent = self.client.beta.assistants.create(model=self.engine, name=self.name, tools=self.load_tools(f'tools/{self.agent_type}.json'), instructions=self.load_prompt(f'prompts/{self.agent_type}.txt'))

    def load_tools(self, file):
        with open(file, 'r') as f:
            return json.load(f)
    
    def load_prompt(self, file):
        with open(file, 'r') as f:
            return f.read()

    def create_thread(self):
        self.thread = self.client.beta.threads.create()

    def create_run(self):
        self.run = self.client.beta.threads.runs.create(thread_id=self.thread.id, assistant_id=self.agent.id)

    def add_message(self, role, message):
        self.client.beta.threads.messages.create(thread_id=self.thread.id, role=role, content=message)

    def add_file(self, file) -> str:
        file = self.client.files.create(file=file, purpose='assistants')
        file = self.client.beta.assistants.files.create(assistant_id=self.agent.id, file_id=file.id)
        return file.id

    def delete_file(self, file):
        self.client.beta.assistants.files.delete(assistant_id=self.agent.id, file_id=file)

    def get_response(self):
        while True:
            retrieved = self.client.beta.threads.runs.retrieve(run_id=self.run.id, thread_id=self.thread.id)
            status = retrieved.model_dump()['status']
            print(f'{self.name} model status: {status}')
            if status == 'completed':
                messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
                )
                return messages.model_dump()['data'][0]['content'][-1]['text']['value']


            elif status == 'requires_action':
                #print(retrieved.model_dump().keys())
                tool_list, run_id, thread_id = self.run_function(retrieved.model_dump())
                #print(f'{name} tool list: {tool_list}')

                self.client.beta.threads.runs.submit_tool_outputs(run_id=run_id, thread_id=thread_id, tool_outputs=tool_list)
                

            elif status == 'failed':
                print(retrieved.model_dump())
                print(f'{self.name} model failed to complete')
                return None

            time.sleep(.25)

    def run_function(self, retrieved):
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
        