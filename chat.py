import openai

def get_response(messages):
    """
    :param messages
    :param messages:
    :return:
    """
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    return response['choices'][0]['message']['content']

def dialogue(mem):
    response = get_response(mem)
    return response