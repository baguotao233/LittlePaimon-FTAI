from typing import Union
from nonebot import on_regex
from nonebot.plugin import PluginMetadata
from nonebot.params import RegexDict
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageSegment
from nonebot.typing import T_State
from LittlePaimon.utils.tool import freq_limiter
from LittlePaimon.utils.filter import filter_msg
from LittlePaimon.manager.plugin_manager import plugin_manager as pm
import requests
from .config import config

__plugin_meta__ = PluginMetadata(
    name='原神语音合成',
    description='原神语音合成',
    usage='...',
    extra={
        'author':   '惜月 / 方糖AI开放平台',
        'version':  '3.0',
        'priority': 8,
    }
)

SUPPORTS_CHARA = ['派蒙']

CHARA_RE = '|'.join(SUPPORTS_CHARA)


def is_paimon(event: Union[GroupMessageEvent, PrivateMessageEvent], state: T_State) -> bool:
    if '_matched_dict' in state:
        if not state['_matched_dict']['chara'] and event.is_tome():
            state['_matched_dict']['chara'] = '派蒙'
        return True
    return False


voice_cmd = on_regex(rf'^(?P<chara>({CHARA_RE})?)说(?P<text>[\w，。！？、：；“”‘’〔（）〕——!\?,\.`\'"\(\)\[\]{{}}~\s]+)',
                     priority=90, block=True,
                     state={
                         'pm_name':        '原神语音合成',
                         'pm_description': 'AI语音合成，让原神角色说任何话！',
                         'pm_usage':       '<角色名>说<话>',
                         'pm_priority':    10
                     }, rule=Rule(is_paimon))

async def token_parser(text):
    if text == "Missing Token":
        return "missing"
    elif text == "Invaild Token":
        return "invaild"
    elif text == "Passed":
        return "pass"

@voice_cmd.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent], regex_dict: dict = RegexDict()):
    regex_dict['text'] = filter_msg(regex_dict['text'].replace('\r', '').replace('\n', ''), '星')
    if not freq_limiter.check(
            f'genshin_ai_voice_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}'):
        await voice_cmd.finish(
            f'原神语音合成冷却中...剩余{freq_limiter.left(f"genshin_ai_voice_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}")}秒')
    freq_limiter.start(f'genshin_ai_voice_{event.group_id if isinstance(event, GroupMessageEvent) else event.user_id}',
                       pm.config.AI_voice_cooldown)
    tokenres = await token_parser(requests.get("https://openai-api-vits-paimon.rdpstudio.top/checktoken?token=" + config.token).text)
    if tokenres == "missing":
        await voice_cmd.finish('合成失败！请联系Bot所有者填写语音合成密钥！')
        return
    elif tokenres == "invaild":
        await voice_cmd.finish('合成失败！请联系Bot所有者填写语音合成密钥！')
        return
    text = str(regex_dict["text"])
    await voice_cmd.finish(MessageSegment.record(
        f'https://openai-api-vits-paimon.rdpstudio.top/generate?text={text}&token={config.token}'))
