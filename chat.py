from openai import OpenAI

def Chat(user_content):
    client = OpenAI(api_key="") # TODO: fill in api_key
    sys_content = """
    You are a research assistant that help me extract time span, metrics and sensor from the user input. Select time span from the list: ["morning","afternoon","night","daytime","whole day"]; select sensor from the list: ["screen","battery"]. If sensor is "screen", select metrics from the list: ["average_duration","total_duration","frequency"]; If sensor is "battery", select metrics from the list: ["decrement","frequency"].
    For example, if user input is " screen usage duration at night", time span is "night", metrics is "duration", sensor is "screen". You should strictly output as follows.(Do not output other words)
    {"time span":"night","metrics":"duration","sensor":"screen"}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":sys_content},
                {"role":"user","content":user_content}]
    )
    return response["choices"][0]["message"]["content"]