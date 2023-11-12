import chromadb
import datetime
import uuid

client = chromadb.PersistentClient(path="VectorDB")
collection = client.create_collection(name='long_term_memory', get_or_create=True)

messages = [
    {"role": "user", "content": "Hi. My name is Alex. I think this is my first time talking to you."},
    {"role": "assistant", "content": "Hi Alex, my name is Thia. Nice to meet you. How's your day going?"},
    {"role": "user", "content": "Busy day. You know, I am an AI application researcher, a job that is usually busy."},
    {"role": "assistant", "content": "Wow, that's cool. Do you enjoy working as an AI application researcher? Or you "
                                     "just feel so so?"},
    {"role": "user", "content": "Yeah, I do enjoy it most of the time. It's fascinating to see how AI can solve "
                                "complex problems. But it can be overwhelming with the amount of learning and keeping"
                                " up to date."},
    {"role": "assistant", "content": "I totally get that. It's a field that's always evolving. Make sure you take "
                                     "some time to unwind as well. What do you do to relax after a long day of work?"},
    {"role": "user", "content": "I usually read or go for a run. Helps to clear my head."},
    {"role": "assistant", "content": "Running is a great way to stay fit and a fantastic stress reliever. Reading "
                                     "anything interesting these days?"}
]

# timestamp = str(datetime.datetime.now().strftime("%y:%m:%d:%H:%M:%S")) # Get the current time. Each entry will be in the format of "role + time" for distinction
# unique_id = str(uuid.uuid4()) # Make the identification even more distinguishable
#
# curr_user_query = messages.pop(-2)
# curr_assistant_query = messages.pop(-1)
#
# curr_user_query_id = "user_" + timestamp + unique_id  # Assign a unique id to the user entry.
# curr_assistant_query_id = "assistant_" + timestamp + unique_id  # Assign a unique id to the user entry.
#
# # Add the entry to the collection
# collection.add(
#     documents=[curr_user_query["content"]],
#     metadatas=[{"role": "user"}],
#     ids=[curr_user_query_id]
# )
# collection.add(
#     documents=[curr_assistant_query["content"]],
#     metadatas=[{"role": "assistant"}],
#     ids=[curr_assistant_query_id]
# )

memory = [
    {"role": "user", "content": "What do I usually do?"}
]

for curr_user_query in memory:
    if curr_user_query["role"] == "user":
        # Check if the content matches the ones in the database to avoid duplications
        historical_assistant_queries = collection.query(
            query_texts=[curr_user_query["content"]],
            where={"role": "assistant"},
            n_results=10
        )
        print(historical_assistant_queries)
        # historical_user_queries = collection.get(
        #     ids=[...],
        #     where={"role": "assistant"},
        #     n_results=10
        # )

print(collection.peek())

historical_user_queries = collection.get(
    ids=['user_23:11:06:23:27:45c616965b-4b11-42a8-b277-b648fda3f3a7'],
    # where={"role": "assistant"},
)
print(historical_user_queries)