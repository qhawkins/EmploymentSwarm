from agent import Agent
from browsing_agent import BrowsingAgent

import asyncio

async def main():
    """agent = Agent('main_agent_1', 'gpt-4-0125-preview', 'coordinator', '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')
    # Load the tools and prompt
    agent.create_agent()
    agent.create_thread()
    agent.add_message('user', 'Hello, I am a user')
    agent.create_run()
    print(agent.get_response())
    """
    browsing_agent = BrowsingAgent('browsing_agent_1', 'gpt-4-vision-preview', 'browser', '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')
    browsing_agent.create_agent()
    browsing_agent.create_thread()
    browsing_agent.add_message('user', 'take a screenshot of https://marketlingo.ai and describe the content of the screenshot.')
    browsing_agent.create_run()
    print(browsing_agent.get_response())


    print('done')
    #agent.add_message('user', 'Hello, I am a user')


if __name__ == '__main__':
    asyncio.run(main())