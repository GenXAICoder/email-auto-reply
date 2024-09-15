import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("gemini_api_key")
# print(api_key)

genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-pro')


def make_reply(email, context="", sentiment="", emotion="", priority=""):
    system_message = "You are automatic email replyer. Write a response to the given email conversation. Respond only with the reply email, nothing else."

    if context:
        system_message += "\n\n" + "This os your current knowledge as an assistant. Adhere to these rules when creating your response:\n\n" + context

    response = model.generate_content(f"You are automatic email replyer. Write a response to the given email conversation. Respond only with the reply email, nothing else.\n\n{context}  Pleae write according to sentiment  {sentiment} and emotion of the email is {emotion}. Priority is {priority}. The number associated with priority states the breifing of the messages. If priority is 1 do less breifing and if priority is > 5 do much breifing. Also the number with higher priority should not be delayed and should be given meeting time just after the day and with less priority should be given meeting time after.  Please write the email according to the sentiment and emotion of the above email".strip() + email)
    return response.text


if __name__ == "__main__":
    reply = make_reply("Hello!\nI would like to book an appointment for a meeting\n\nBest,\nMe")
    print(reply)
    


