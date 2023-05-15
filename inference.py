import requests


def preprocess(text):
    text = text.replace("\n", "\\n").replace("\t", "\\t")
    return text


def postprocess(text):
    return text.replace("\\n", "\n").replace("\\t", "\t").replace('%20', '  ')


def chat(input_text, sample=True, max_length=512, top_p=1, temperature=0.7, user=[], gen=[], top_k=None, repetition_penalty=None, max_time=None):
    # return input_text
    if len(user) > 5:
        user = user[-5:]
        gen = gen[-5:]

    # print(user)
    # print(gen)

    context = "\n".join(
        [f"用户：{user[i]}\n小元：{gen[i]}" for i in range(len(user))])
    text = f'{context}\n用户：{input_text}\n小元：'
    text = text.strip()
    text = preprocess(text)

    # print('input_text:', text)

    model_id = 'llllhd/ChatCare-RLHF'
    api_token = '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'
    api_url = f'https://api-inference.huggingface.co/models/{model_id}'
    headers = {"Authorization": f"Bearer {api_token}"}

    payload = {
        'inputs': text,
        'parameters': {
            'do_sample': sample,
            'max_length': max_length,
            'top_p': top_p,
            'top_k': top_k,
            'temperature': temperature,
            'repetition_penalty': repetition_penalty,
            'max_time': max_time,
        },
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print('response:', response)
        if response.status_code == 200:
            return postprocess(response.json()[0]['generated_text'])
        elif response.status_code == 503:
            return 503
        else:
            return None
    except:
        return None


if __name__ == '__main__':
    print(chat('你好'))
