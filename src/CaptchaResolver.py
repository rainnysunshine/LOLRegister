import requests
from loguru import logger
from constants import api_url,api_key

class CaptchaResolver(object):

    def __init__(self):
        self.api_url = api_url
        self.api_key = api_key

    def create_task(self, question, queries):
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "HCaptchaClassification",
                "question": question,
                "queries": queries
            }
        }

        try:
            response = requests.post(self.api_url, json=data, timeout=60)
            result = response.json()
            logger.debug(f'captcha recognize result {result}')
            return result
        except requests.RequestException:
            logger.exception(
                'error occurred while recognizing captcha', exc_info=True
            )

if __name__ == '__main__':
    api_url = 'https://api.yescaptcha.com/createTask'