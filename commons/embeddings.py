import chromadb
import datetime
from chromadb.utils import embedding_functions

def init_vdb():
    """
    Initializes the vector database.
    """
    client = chromadb.PersistentClient(path="vectorDB")

    try:
        collection = client.get_collection("vectorDB")
    except:
        collection = client.create_collection(
            name="vectorDB",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(device="cpu"),
            metadata={
                "hnsw:space": "cosine",
            }
        )

    return collection


def create_embedding(collection, mem):
    """
    Create an embedding for each message.
    :param collection:
    :param mem:
    """
    # Create an unique id for each message
    ai_ids = []
    human_ids = []
    ai_meta = []
    human_meta = []
    ai_msg_db = []
    human_msg_db = []
    count = -1
    date = datetime.datetime.now().strftime("%y:%m:%d:%H:%M:%S")

    if len(mem) == 1:
        return collection
    else:
        for i, k in zip(mem[::2], mem[1::2]):
            # Create a unique ID for each message
            count += 1
            ai_ids.append("ai_msg_" + str(date) + str(count))
            human_ids.append("human_msg_" + str(date) + str(count))
            ai_meta.append({"role": "assistant", "date": str(date), "count": str(count)})
            human_meta.append({"role": "user",  "date": str(date),  "count": str(count)})
            # Store the message pair in a list
            human_msg_db.append(str(k["content"]))
            ai_msg_db.append(str(i["content"]))

            # print(msg_db)
            # Add docs to the collection. Can also update and delete. Row-based API coming soon!
            collection.add(
                documents=ai_msg_db,
                metadatas=ai_meta,
                ids=ai_ids,  # unique for each doc
            )

            collection.add(
                documents=human_msg_db,
                metadatas=human_meta,
                ids=human_ids,  # unique for each doc
            )

            return collection


def search_embedding(collection, mem, n_results):
    """
    Search for similar messages in the database.
    """

    # Create an unique id for each message
    ai_msg_db = []
    human_msg_db = []

    if len(mem) == 1:
        human_msg_db.append(str(mem[0]["content"]))

    else:
        for i, k in zip(mem[::2], mem[1::2]):
            # Store the message pair in a list
            human_msg_db.append(str(k["content"]))
            ai_msg_db.append(str(i["content"]))

    print(ai_msg_db)
    print(human_msg_db)

    ai_results = collection.query(
        query_texts=human_msg_db,
        n_results=n_results,
        where={"role": "assistant"}  # optional filter
        # where_document={"$contains":"search_string"}  # optional filter
    )

    human_id_list = []
    human_msg_list = []
    print(ai_results["ids"][0])

    for index, i in enumerate(ai_results["ids"][0]):
        new_i = i.replace("ai_msg_", "human_msg_")
        # print(new_i)
        human_id_list.append(new_i)

    print(human_id_list)

    for i in human_id_list:
        human_results = collection.get(
            ids=[i]
        )
        human_msg_list.append(human_results["documents"])

    return ai_results, human_msg_list

"""
# Test
collection = init_vdb()
ai, human = search_embedding(collection, "Bad day", 3)

for i in ai["documents"][0]:
    print(i)

for i in human:
    print(i)
"""

"""
collection = init_vdb()

user_query = "Bad day"
mem = [
    {"role":"user","content":"I'm having a really tough day!"},
    {"role":"assistant","content":"That's really sad! Would you mind to share it with me?"},
]

# create_embedding(collection, mem)

search = search_embedding(collection,user_query,3)
print(type(search))
# print(search)

for i in search:
    for ii in i:
        print(ii)
"""
