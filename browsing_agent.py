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
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
		
	
	async def load_page(self, url: str):
		self.driver.get(url)
		return f"Webpage at {url} successfully loaded, continue to next step."

	async def view_page(self): 
		screenshot = self.driver.get_screenshot_as_png()

		screenshot = base64.b64encode(screenshot).decode('utf-8')
		print("screenshot taken")
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
			temperature=0
		)
		print("screenshot response created")
		return response.choices[0].message.content
	
	async def move_cursor(self, x: int, y: int):
		pyautogui.moveRel(x, y, duration=1.2)
		return f"Cursor moved relative to the past position by {x} pixels in the x direction and {y} pixels in the y direction."

	async def get_url(self):
		return self.driver.current_url

	async def get_ai_response(self, message_list):
		response_generator = await self.client.chat.completions.create(
		model=self.engine,
		messages=message_list,
		stream=True,
		tools=self.tools,
		tool_choice='auto',
		temperature=0
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
						print(tool_args)
						try:
							old_tool_args = tool_args
							tool_args = ''.join(tool_args)
							tool_args = json.loads(tool_args)
						except:
							tool_args = old_tool_args
							continue

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

	async def get_cursor_position(self):
		return str(pyautogui.position())

	async def find_clickable_elements(self):
		WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
		clickable_elements_selectors = [
			(By.TAG_NAME, 'a'),
			(By.TAG_NAME, 'button'),
			# Adding tuples for XPath-based selectors
			(By.XPATH, "//*[@onclick]"),  # Elements with an 'onclick' attribute
			(By.XPATH, "//*[@role='button']"),  # Elements with a role attribute set to 'button'
		]

		clickable_elements_names = []

		for selector_type, selector_value in clickable_elements_selectors:
			elements = self.driver.find_elements(selector_type, selector_value)
			for element in elements:
				name_or_text = element.text.strip() or element.get_attribute('name') or element.get_attribute('value')
				if name_or_text:  # Ensure the name or text is not empty
					clickable_elements_names.append(name_or_text)
		
		return clickable_elements_names

	async def click_element(self, element_name):
		element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{element_name}')]")
		try:
			element.click()
		except:
			return f"Element with name '{element_name}' not clickable."
		
		return f"Element with name '{element_name}' clicked."
			

	async def go_to_coords(self, x, y):
		pyautogui.moveTo(x, y, duration=1.2)
		return f"Cursor moved to coordinates {x}, {y}."
	
	async def find_text_elements(self):
		element_descriptions = []

		# XPath to select all <input> elements and <textarea> elements
		elements_xpath = "//input[not(@type='button') and not(@type='submit') and not(@type='reset') and not(@type='checkbox') and not(@type='radio') and not(@type='file') and not(@type='hidden') and not(@type='image')] | //textarea"

		# Find elements matching the XPath
		elements = self.driver.find_elements(By.XPATH, elements_xpath)

		for element in elements:
			# Attempt to extract various attributes if available
			element_id = element.get_attribute('id')
			element_class = element.get_attribute('class')
			element_type = element.get_attribute('type') or "textarea"  # Default to textarea if type attribute is missing
			element_value = element.get_attribute('value')
			element_name = element.get_attribute('name')
			element_placeholder = element.get_attribute('placeholder')

			# Build a description string based on available attributes
			description_parts = [f"Type: {element_type}", f"ID: {element_id}", f"Class: {element_class}", 
								f"Name: {element_name}", f"Value: {element_value}", f"Placeholder: {element_placeholder}"]
			# Filter out empty parts
			description = ', '.join(filter(None, description_parts))

			if description:  # Ensure the description is not empty
				element_descriptions.append(description)

		return element_descriptions


	
	async def enter_text(self, element_id, text):
		# Try finding an input element with the specified name attribute
		try:
			element = self.driver.find_element(By.ID, element_id)
		except:
			# If not found by name, try finding a textarea by name as a fallback
			# If still not found, raise an error or handle it as needed
			raise f"Element with id '{element_id}' not found."
		
		element.clear()  # Clear the text field before entering text
		element.send_keys(text)
		return f"Text '{text}' entered into element with id '{element_id}'."

	async def find_recaptcha_site_key(self):
		try:
			# First, wait for the iframe to be present, if any, and switch to it
			WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
			iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
			
			for iframe in iframes:
				self.driver.switch_to.frame(iframe)
				try:
					# Within each iframe, try to find the reCAPTCHA element
					recaptcha_element = WebDriverWait(self.driver, 5).until(
						EC.presence_of_element_located((By.XPATH, '//*[@data-sitekey]'))
					)
					site_key = recaptcha_element.get_attribute('data-sitekey')
					print(f"Found site key: {site_key}")
					return site_key
				except:
					# If not found in this iframe, switch back and try the next one
					self.driver.switch_to.default_content()
					continue
				finally:
						# Ensure we switch back to the default content before trying the next iframe or finishing
					self.driver.switch_to.default_content()
				
			# If not found in any iframe, try to find the reCAPTCHA element directly in the main page
			recaptcha_element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.XPATH, '//*[@data-sitekey]'))
			)
			site_key = recaptcha_element.get_attribute('data-sitekey')
			print(f"Found site key: {site_key}")
			return site_key

		except Exception as e:
			print("Could not find the reCAPTCHA site key on this page.")
			print(e)
			return None


	async def solve_captcha(self):
		site_key = None
		try:
			recaptcha_element = self.driver.find_element(By.XPATH, '//*[@data-sitekey]')
		
			site_key = recaptcha_element.get_attribute('data-sitekey')
			print(f"Found site key: {site_key}")
		except Exception as e:
			print("Could not find the reCAPTCHA site key on this page.")
			print(e)
		
		if site_key==None:
			site_key = await self.find_recaptcha_site_key()

		api_key = "86089cd56483af8dff5acb9255d887b4"

		form = {"method": "userrecaptcha",
		"googlekey": site_key,
		"key": api_key,
		"pageurl": self.driver.current_url,
		"json": 1}

		response = requests.post('http://2captcha.com/in.php', data=form)
		request_id = response.json()['request']

		status = 0
		url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
		while not status:
			res = requests.get(url)
			if res.json()['status']==0:
				time.sleep(3)
			else:
				requ = res.json()['request']
				js = f'document.getElementById("g-recaptcha-response").innerHTML="{requ}";'
				self.driver.execute_script(js)
				self.driver.find_element(By.ID, "recaptcha-demo-submit").submit()
				status = 1

		return "Captcha solved."


	async def run_functions(self, function_name, function_args):
		if function_name == 'view_page':
			response = await self.view_page()
			
		elif function_name == 'move_cursor':
			response = await self.move_cursor(**function_args)
			
		elif function_name == 'load_page':
			response = await self.load_page(**function_args)
			
		elif function_name == 'end_conversation':
			response = await self.end_conversation()
			self.conversation = False
		
		elif function_name == 'get_cursor_position':
			response = await self.get_cursor_position()
		
		elif function_name == 'get_url':
			response = await self.get_url()
		
		elif function_name == "find_clickable_elements":
			response = await self.find_clickable_elements()

		elif function_name == 'go_to_coords':
			response = await self.go_to_coords(**function_args)
		
		elif function_name == 'click_element':
			response = await self.click_element(**function_args)

		elif function_name == 'find_text_elements':
			response = await self.find_text_elements()
		
		elif function_name == 'enter_text':
			response = await self.enter_text(**function_args)
		
		elif function_name == 'solve_captcha':
			response = await self.solve_captcha()


		return response

	async def call_function(self, func_call):
		responses = {}
		for function_name, function_args in func_call.items():
			if function_name == "multi_tool_use.parallel":
				for function_name, function_args in function_args.items():
					responses[function_name] = await self.run_functions(function_name, function_args)
				return responses
			
			responses[function_name] = await self.run_functions(function_name, function_args)
		return responses
	
	   
	async def create_run(self, message):
		self.conversation = True
		text_storage = ""
		self.message_list.append({'role': 'user', 'content': message})
		while self.conversation==True:
			text_storage = ''
			initial_response = True
			#print(chat_history)
			async for text, function_flag, function_responses in self.get_ai_response(self.message_list):
				#print(chat_history)
				if text != None:
					if initial_response:
						initial_response = False
					text_storage = text_storage + text
				if function_flag:
					text_storage = text_storage + "These are the tool call results: " + str(function_responses)
			
			self.message_list.append({'role': 'user', 'content': text_storage})
			

			
		
	def retrieve_messages(self):
		return self.message_list
	
