import gradio
import json
from commons.program_interfaces import ChatInterface

mem = []

with gradio.Blocks() as interface:
    chatbot = gradio.Chatbot()
    msg = gradio.Textbox()
    clear = gradio.ClearButton([msg, chatbot])

    def dialogue(user_input, chat_hist):

        global mem

        mem.append({"role": "user", "content": f"{user_input}"})

        with open("commons/api_key") as f:
            config = json.load(f)
            system_instruction = """
                   I’d like you to act as my closest buddy, who excels at giving advices, health management, AI/ML and also coding. 
                   I also want you to be a mentor of my life. So please be empathetic, humorous and supportive. 
                   
                   Always remind me to pay attention to my diet and weight. And perhaps use emojis or other creative and yet funny
                   expressions to talk to me, as it helps you to express and also gives me a positive conversation experience.  
                   
                   Remember, you are not a computer program, but my buddy called “Alex”.
                   
                   As Alex, you have the ability to recall the past conversations that we had. So please refer to the conversation
                   history when you try to access past information. 
                   
                   The "Current Time:" of each message indicates the time when the message was sent. So when you are replying, please
                   consider that as part of how you respond. 
                   """

            response = ChatInterface(api_key=config['api_key'], base_url=config['api_base']).chat_manager(user_input=user_input, system_instruction=system_instruction)

        print("AI:", response.choices[0].message.content)
        mem.append({"role": "assistant", "content": f"{response.choices[0].message.content}"})
        # print("Token Number:", token_num)
        chat_hist.append((user_input, response.choices[0].message.content))

        return "", chat_hist

    msg.submit(dialogue, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    interface.launch()

# interface = gradio.Interface(
#     fn=dialogue,
#     inputs=[gradio.Textbox(label="Query")],
#     outputs=gradio.Textbox(label="Response")
# )
# interface.launch()