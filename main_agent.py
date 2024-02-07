from openai import AsyncOpenAI
from agent import Agent

class MainAgent(Agent):
    def __init__(self):
        super().__init__(self)
        self.client = AsyncOpenAI()