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
    browsing_agent = BrowsingAgent('browsing_agent_1', 'gpt-4-turbo-preview', 'browser', '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')
    print(await browsing_agent.create_run('View the webpage https://marketlingo.ai and tell me what you see. Click on the element on the page that you find most interesting and tell me about it.'))

    #await browsing_agent.create_run('Hello, I am a user')
    #print(browsing_agent.retrieve_messages())

    print('done')
    #agent.add_message('user', 'Hello, I am a user')


if __name__ == '__main__':
    asyncio.run(main())