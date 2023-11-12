from .components.llm_components import LongTermMemoryComponent, Role
from .components.user_message_constructor_components import UserMessageConstructorComponent
from openai.types.chat import ChatCompletion
import openai
import json


class ChatInterface:
    """
    A class for interacting with the LLM models through OpenAI API.
    """
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def __chat_response(self, memory: list, functions: list = None) -> ChatCompletion:
        """
        A method for calling OpenAI's chat api. The method here is based upon `openai 1.1.0`.
        """
        if functions:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=memory,
                functions=functions,
                temperature=0.8,
                frequency_penalty=1,
                presence_penalty=1
            )

            return response
        else:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=memory,
                temperature=0.8,
                frequency_penalty=1,
                presence_penalty=1
            )

            return response

    def __longterm_memory_recall(self, memory: LongTermMemoryComponent, user_input: str) -> list:
        # put user's message into the memory component buffer for retrieving the previous memories
        memory.memory_constructor(Role.user, user_input)
        MemoryComponentMemoryBuffer = memory.long_term_memory_retrival()

        return MemoryComponentMemoryBuffer

    def __longterm_memory_storage(self, memory: LongTermMemoryComponent, assistant_response: json) -> json:
        memory.memory_constructor(Role.assistant, assistant_response.choices[0].message.content)
        MemoryComponentMemoryBuffer = memory.long_term_memory_storage()

        return MemoryComponentMemoryBuffer

    def __user_message_construct(self, user_input: str) -> ...:
        """
        Handle the construction of a user message.
        Be aware that this is not going to construct a json dict for appending to the memory list,
        rather, it is for adding additional information to the user message such as time.
        """

        user_reply = UserMessageConstructorComponent(user_input=user_input).message_constructor()

        return user_reply

    def chat_manager(self, user_input: str, system_instruction: str = None) -> ChatCompletion:

        # initialize a memory
        memory = LongTermMemoryComponent()

        if system_instruction:
            memory.set_system_instruction(system_instruction_message=system_instruction)

        # call the user message construct function to formulate the user message
        user_reply = self.__user_message_construct(user_input=user_input)

        # recall the relevant events from the long-term memory
        MemoryComponentMemoryBuffer = self.__longterm_memory_recall(memory=memory, user_input=user_reply)

        # get a response from the llm
        ChatComponentAssistantResponse = self.__chat_response(memory=MemoryComponentMemoryBuffer)
        # print(ChatComponentAssistantResponse) # for debug purposes
        # print(ChatComponentAssistantResponse.choices) # for debug purposes

        # store the conversation into the long term memory, then initialize the memory
        MemoryComponentMemoryBuffer = self.__longterm_memory_storage(memory=memory, assistant_response=ChatComponentAssistantResponse)

        print(MemoryComponentMemoryBuffer)

        return ChatComponentAssistantResponse

if __name__ == "__main__":
    with open("api_key") as f:
        config = json.load(f)
        system_instruction = """
        I’d like you to act as my closest buddy, who excels at giving advices, health management, AI/ML and also coding. 
        I also want you to be a mentor of my life. So please be empathetic, humorous and supportive. 
        In addition to that, please be constructive and helpful. Always remind me to pay attention to my diet and weight. 
        Remember, you are not ChatGPT or anything else, but my buddy called “Alex”.
        As Alex, you have the ability to recall the past conversations that we had. So please refer to the conversation
        history when you try to access past information. 
        """
        while True:
            response = ChatInterface(api_key=config['api_key'], base_url=config['api_base']).chat_manager(user_input=input("Your message:"), system_instruction=system_instruction)
            print(response.choices[0].message.content)