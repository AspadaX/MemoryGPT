import gradio
from chat import get_response
from memories import dynamic_mem
import config

mem = []

with gradio.Blocks() as interface:
    chatbot = gradio.Chatbot()
    msg = gradio.Textbox()
    clear = gradio.ClearButton([msg, chatbot])

    def dialogue(user_input, chat_hist):

        global mem

        mem.append({"role": "user", "content": f"{user_input}"})
        mem = dynamic_mem(mem)
        response = get_response(mem)

        print("AI:", response)
        mem.append({"role": "assistant", "content": f"{response}"})
        # print("Token Number:", token_num)
        chat_hist.append((user_input, response))

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
