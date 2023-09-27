import tiktoken
import embeddings

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """
    Return the number of tokens used by a list of messages.
    """
    encoding = tiktoken.encoding_for_model(model)
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def dynamic_mem(mem):
    """
    This function is used to dynamically update the memory.
    """
    if mem[0]["role"] != "system":
        mem.insert(0, {"role": "system", "content": "You are a personal assistant who's name is Thia. When you respond to me, please consider the context of our conversation before responding."})
        # mem.insert(1, {"role": "assistant", "content": "Hello, how was your day?"})
        print(mem)
    else:
        pass

    if len(mem) > 1 and num_tokens_from_messages(mem) <= 2500: # Short-term memory

        if mem[0]["role"] == "system":
            del mem[0]
        else:
            pass

        collection = embeddings.init_vdb()
        human_msgs, ai_msgs = embeddings.search_embedding(collection=collection, mem=mem, n_results=5)

        if len(mem) == 1:
            msg_2 = mem[-1]
            pass
        else:
            msg_2 = mem[-1]
            del mem[-1]
            embeddings.create_embedding(collection=collection, mem=mem)
            print(ai_msgs, human_msgs)

        for ai_msg, human_msg in zip(ai_msgs, human_msgs["documents"][0]):
            msg_1 = {"role": "user", "content": f"{human_msg}"}
            msg = {"role": "assistant", "content": f"{ai_msg[0]}"}
            print(msg_1)
            print(msg)
            mem.insert(1, msg_1)
            mem.insert(2, msg)
            # mem.append(msg_1)
            # mem.append(msg)

        mem.insert(0, {"role": "system", "content": "You are a personal assistant who's name is Thia. When you respond to me, please consider the context of our conversation before responding."})

        if len(mem) == 2:
            pass
        else:
            mem.append(msg_2)

        print(mem)
        return mem

    elif len(mem) > 1 and num_tokens_from_messages(mem) > 2500: # Long-term memory

        if mem[0]["role"] == "system":
            del mem[0]
        else:
            pass

        message = mem[-1]["content"]
        collection = embeddings.init_vdb()
        embeddings.create_embedding(collection=collection, mem=mem)
        human_msgs, ai_msgs = embeddings.search_embedding(collection=collection, mem=mem, n_results=10)
        count = -1

        mem = [
            {"role": "user", "content": f"{message}"}
        ]

        for ai_msg, human_msg in zip(ai_msgs["documents"][0], human_msgs):
            count += 1
            msg_1 = {"role": "user", "content": f"{human_msg}"}
            msg = {"role": "assistant", "content": f"{ai_msg[0]}"}
            mem.insert(count, msg_1)
            mem.insert(count+1, msg)

        if mem[0]["role"] != "system":
            mem.insert(0, {"role": "system", "content": "You are a personal assistant who's name is Thia. When you respond to me, please consider the context of our conversation before responding."})
        else:
            pass

        print(mem)
        return mem

    else:
        return mem
        print(mem)

# # testing the functions
# mem = [
#     {"role": "user", "content": "I am feeling down."},
#     {"role": "assistant", "content": "Oh! What has happened to you?"},
#     {"role": "user", "content": "Just a tiresome day..."},
#     {"role": "assistant", "content": "I am sorry to hear that."}
# ]
# mem, token_num = short_term_mem("No worries. I'm good.","I hope you will be doing well.",mem=mem)
# print(mem)
# print(token_num)