from openai import AsyncOpenAI

class Agent:
    def __init__(self):
        self.client = AsyncOpenAI()

    def get_response(self, prompt):
        return self.client.get_response(prompt)

    def train(self, prompt, response):
        return self.client.train(prompt, response)
