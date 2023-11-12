import uuid
import chromadb
import datetime
import requests
import json
from enum import Enum

class Role(Enum):
    """
    Enum Class for the roles of the chatbot
    """
    user = 1
    assistant = 2
    system = 3
    observation = 4

class MemoryComponent:
    """
    Handle the memory in general.
    """

    def __init__(self):
        self.memory = []
        self.system_instruction = None

    def set_system_instruction(self, system_instruction_message: str = None) -> None:
        """
        Determines if the system_instruction is needed.

        :return:
        """
        # Determine if the system_instruction is needed.
        if not self.system_instruction:
            system = {"role": "system", "content": system_instruction_message}
            self.system_instruction = system_instruction_message
            self.memory.insert(0, system)
        elif self.system_instruction:
            pass
        else:
            raise ValueError("System instruction encounters error.")

class LongTermMemoryComponent(MemoryComponent):
    """
    Handle the long-term memory of the large language model.
    """
    client = chromadb.PersistentClient(path="./VectorDB")
    collection = client.create_collection(name='long_term_memory', get_or_create=True)

    def __init__(self):
        super().__init__()

    def __long_term_memory_storage_preprocessor(self) -> tuple[dict, dict, str, str]:
        """
        Preprocess the memory before passing them into the storage process.
        @rtype: object
        """

        # pop out the system instruction from the memory
        if self.system_instruction:
            self.system_instruction = self.memory.pop(0)

        # Get the current time. Each entry will be in the format of "role + time" for distinction
        timestamp = str(datetime.datetime.now().strftime("%y:%m:%d:%H:%M:%S"))

        # Make the identification even more distinguishable with UUID
        unique_id = str(uuid.uuid4())

        # Get the current user and assistant query
        curr_user_query = self.memory.pop(-2)
        curr_assistant_query = self.memory.pop(-1)

        # Generate corresponding ids for the current user and assistant query
        curr_user_query_id = "user_" + timestamp + unique_id  # Assign a unique id to the user entry.
        curr_assistant_query_id = "assistant_" + timestamp + unique_id  # Assign a unique id to the user entry.

        return curr_user_query, curr_assistant_query, curr_user_query_id, curr_assistant_query_id

    def __long_term_memory_redundancy_checker(self, curr_assistant_query) -> bool:
        """
        If the assistant's message is exactly the same as one of the previously stored message,
        we will not store it.

        @return: bool
        """

        # Lookup in the long_term_memory
        historical_assistant_queries = self.collection.get(
            where_document={"$contains": curr_assistant_query['content']}
        )

        # See if it matches any of the historical assistant queries
        if historical_assistant_queries['ids']:
            return True
        else:
            return False

    def long_term_memory_storage(self) -> list:
        """
        For storing memories into the long-term memory database.
        """

        # Get `curr_user_query`, `curr_assistant_query`, `curr_user_query_id` and `curr_assistant_query_id`
        curr_user_query, curr_assistant_query, curr_user_query_id, curr_assistant_query_id = self.__long_term_memory_storage_preprocessor()

        # Check if the current assistant query is redundant
        redundancy = self.__long_term_memory_redundancy_checker(curr_assistant_query)

        if not redundancy:
            # Add the entry to the collection, if the assistant query is not redundant
            self.collection.add(
                documents=[curr_user_query["content"]],
                metadatas=[{"role": "user"}],
                ids=[curr_user_query_id]
            )
            self.collection.add(
                documents=[curr_assistant_query["content"]],
                metadatas=[{"role": "assistant"}],
                ids=[curr_assistant_query_id]
            )

        # Empty the memory before assigning the system_instruction
        self.memory = []

        if self.system_instruction:
            # Assign the system_instruction and curr_user_query
            self.memory.append(self.system_instruction)

        return self.memory

    def long_term_memory_retrival(self) -> list:
        """
        For retrieving memories from the collection
        """
        if self.system_instruction:
            self.system_instruction = self.memory.pop(0)

        # Get the current user query
        curr_user_query = self.memory.pop(-1)
        print("curr_user_query:", curr_user_query)

        # Check if the role matches user. We use user messages to match the relevant memories.
        if curr_user_query["role"] == "user":
            historical_assistant_queries = self.collection.query(
                query_texts=[curr_user_query["content"]],
                where={"role": "assistant"},
                n_results=10
            )
            print("historical_assistant_queries:", historical_assistant_queries)
            # Use the ids to get the paired assistant memories.
            for id, query_text in zip(historical_assistant_queries['ids'][0], historical_assistant_queries['documents'][0]):
                historical_user_queries_id = id.replace("assistant_", "user_", 1)
                historical_user_queries = self.collection.get(
                    ids=[historical_user_queries_id],
                    # where={"role": "assistant"},
                )
                self.memory_constructor(role=Role.user, content=historical_user_queries['documents'][0]) # Append the user query first
                self.memory_constructor(role=Role.assistant, content=query_text) # Then we append the assistant query
        else:
            raise ValueError

        if self.system_instruction:
            # Assign the system_instruction and curr_user_query
            self.memory.insert(0, self.system_instruction)

        self.memory.append(curr_user_query)

        return self.memory

    def memory_constructor(self, role: Role = None, content: str = None) -> list:
        """
        Construct the memory

        :param:
        :return:
        """
        message = {"role": role.name, "content": content}
        self.memory.append(message)
        print("curr_memory:", self.memory)

        return self.memory

class FunctionCallComponent:

    def __init__(self):
        pass

    def call_function(self, response: json) -> getattr:
        """
        determine which function to call

        @param response:
        @return:
        """
        arguments = self.__retrieve_arguments(response=response)
        function_name: str = self.__retrieve_function_name(response=response)

        return getattr(self, function_name)(arguments)

    def __retrieve_function_name(self, response: json) -> str:
        """
        retrieve the function name from the response we get from LLM

        @rtype: object
        @param response:
        @return:
        """
        function_name = response.choices[0].message.function_call.name

        return function_name

    def __retrieve_arguments(self, response: json) -> dict:
        """
        retrieve the functional json from the response we get from LLM

        @param response:
        @return:
        """
        arguments = json.loads(response.choices[0].message.function_call.arguments)

        return arguments

    def get_current_weather(self, arguments: dict) -> dict:

        location = arguments['location']

        url = f"https://wttr.in/{location}?format=j1"
        api_response = requests.get(url)

        if api_response.status_code == 200:
            function_response = api_response.json()
            # print(data)
            return function_response
        else:
            print("Error:", api_response.status_code)


if __name__ == "__main__":
    # client = chromadb.PersistentClient(path="/Users/xinyubao/Documents/pyR/bluelight-project/VectorDB")
    # collection = client.create_collection(name='long_term_memory', get_or_create=True)

    ...
