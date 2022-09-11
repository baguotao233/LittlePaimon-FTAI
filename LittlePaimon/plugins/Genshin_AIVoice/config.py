from typing import Dict
from LittlePaimon.config import AI_CONFIG
from LittlePaimon.utils.files import load_yaml, save_yaml


class AIConfig:
    def __init__(self):
        if AI_CONFIG.exists():
            data = load_yaml(AI_CONFIG)
        else:
            data = {}
        self.token: str = data.get('密钥', '请在 https://www.yuque.com/launchpad/kwmwcs/masia7 处申请')


config = AIConfig()
