import string
from secrets import choice as secrets_choice

from user_agents import parse


def generate_random_string():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets_choice(alphabet) for _ in range(16)) 


def get_device_type(user_agent: str):
    user_agent = parse(user_agent)
    if user_agent.is_pc:
        return 'pc'
    if user_agent.is_tablet:
        return 'tablet'
    if user_agent.is_mobile:
        return 'mobile'
    return 'other'
