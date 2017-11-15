import requests


def beary_chat(text, user=None):
    requests.post(
        # 'https://hook.bearychat.com/=bw8NI/incoming/ab2346561ad4c593ea5b9a439ceddcfc',
        'https://hook.bearychat.com/=bw8Zi/incoming/87be25d4108a2a2838e1809d3b6b54a8',
        json={
            "user": user,
            'text': text
        }
    )