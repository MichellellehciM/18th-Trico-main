from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def simplified_time_ago(value):
    if not value:
        return "未知時間"
    delta = now() - value
    days = delta.days
    seconds = delta.seconds

    if days > 0:
        return f"{days} 天前"
    elif seconds >= 3600:
        return f"{seconds // 3600} 小時前"
    elif seconds >= 60:
        return f"{seconds // 60} 分鐘前"
    else:
        return "剛剛"
