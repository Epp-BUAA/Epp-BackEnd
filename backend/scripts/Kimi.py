import openai

openai.api_base = "https://api.sanyue.site/v1"
openai.api_key = 'sk-RHa0NhwUiZCPu4vt06A0368e10624e348233D60aB799Bc11'

if __name__ == '__main__':
    history = []
    while True:
        user_input = input("用户：")
        history.append({"role": "user", "content": user_input})
        if user_input.lower() == "exit":
            break
        response = openai.ChatCompletion.create(
            model="kimi",
            messages=history,
            stream=False
        )
        if response.code == 200:
            print(response.choices[0].message.content)
        else:
            print(response)