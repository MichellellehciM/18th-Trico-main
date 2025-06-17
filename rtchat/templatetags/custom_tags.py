# rtchat/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.simple_tag
def unique_chat_partners(user):
    seen = set()
    results = []

    for chatroom in user.chat_groups.filter(is_private=True):
        for member in chatroom.members.exclude(id=user.id):
            if member.id not in seen:
                seen.add(member.id)
                results.append((chatroom.group_name, member.username))
    return results
