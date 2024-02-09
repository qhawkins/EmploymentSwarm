from agent import Agent
from selenium import webdriver
import time
import json
from agent_tools import tools
import base64

class BrowsingAgent(Agent):
    def __init__(self, name, engine, agent_type, api_key):
        super().__init__(name, engine, agent_type, api_key)

        self.driver = webdriver.Chrome()
    
    def take_screenshot(self, url: str):
        self.driver.get(url)
        #time.sleep(1)
        screenshot = self.driver.get_screenshot_as_base64()
        screenshot = str.encode(screenshot)
        file_id = self.add_file(screenshot)
#        self.client.images.create_variation(file_id, 'screenshot', 'assistants')
        return "Screenshot added to knowledge with id of " + file_id

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
            
            elif elem['function']['name'] == 'take_screenshot':
                response = self.take_screenshot(url=arguments['url'])
                print(response)

            else:
                response = 'No response, invalid function'
                print(response)
                exit()
                
            tool_list.append({'tool_call_id': str(tool_id), 'output': str(response)})
            
        return tool_list, run_id, thread_id