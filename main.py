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
    #await browsing_agent.load_page('https://marketlingo.ai')
    #print(await browsing_agent.find_text_elements())
    #exit()

    await browsing_agent.create_run('View the webpage https://marketlingo.ai. Click on the "FAQs" link. After that, click on the "Home" link to go back to the homepage. After that, fill out all of the text fields for the "contact us" form and submit the form.')
    messages = browsing_agent.retrieve_messages()
    for x in messages:
        print(x)

    #await browsing_agent.create_run('Hello, I am a user')
    #print(browsing_agent.retrieve_messages())

    print('done')
    #agent.add_message('user', 'Hello, I am a user')


if __name__ == '__main__':
    asyncio.run(main())