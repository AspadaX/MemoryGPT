# Digital Life Project

An open-source weekend fun project aims to make LLMs more like a human. 

## Overview

This project implements a conversational AI assistant, who possesses long-term memories, that can track context and refer back to previous conversations, even if the conversation happened days ago or sessions ago. It utilizes the OpenAI libray for text generation paired with vector similarity search to find relevant passages from prior chat history.

Be aware that you can actually use the OpenAI extension of Text Generation WebUI to use this project with your own LLM. I tested this project with a Vicuna 13B 16K model. 

The assistant is built in a modular way, separating the UI, API calls, memory management, and content generation. Key features:

- Web interface for chatting via Gradio 
- Conversation memory tracking
- Retrieval of old messages via vector embeddings
- Dynamic memory truncation based on context length
- Modular components for extensibility

## Usage

To use this assistant:

1. Install python libraries: `ChromaDB` and `OpenAI`
2. Obtain OpenAI API keys and add to `config.py`
3. Run `WebUI.py` to launch the web interface
4. Chat with the assistant in your browser

The assistant will track context, refer to old messages, and truncate memory when needed.

## Files

- `chat.py`: OpenAI ChatCompletion API interface 
- `config.py`: API keys 
- `embeddings.py`: Manages message embeddings for similarity search  
- `memories.py`: Conversation memory manager
- `WebUI.py`: Web interface with Gradio

## To Do

Some ideas for extending this project:

- Integrate with another LLM-related project of mine - Thinker (https://github.com/AspadaX/Thinker_DecisionMakingAssistant)
- Being able to perform agent actions, such as search the Internet etc.
- A more human-like conversation style.
- Being able to export and import memories.
- And more!

## Credit

- ChromaDB, the backbone of this project's vector database.
- Text Generation WebUI OpenAI Extension, I tested the OpenAI api with this extension and loaded a small LLM with the WebUI.
- Vicuna 13B 16K, I used this LLM for testing. 

## License

This project is open source and available under the [MIT License](LICENSE).

Let me know if you would like any changes or have additional sections to add!
