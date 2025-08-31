from django import template
from django.utils.safestring import mark_safe
import re
from django.utils.html import conditional_escape

register = template.Library()




@register.filter(name='censor', needs_autoescape=True)
def censor_filter(value, autoescape=True):


   if not value:
      return value

   # Список нежелательных слов
   forbidden_words = [
      'дурак', 'дебил', 'тупой'
   ]

   if autoescape:
      value = conditional_escape(value)

   pattern = r'\b(' + '|'.join(re.escape(word) for word in forbidden_words) + r')\b'

   def replace_match(match):
      word = match.group(0)

      if len(word) > 2:
         return word[0] + '*' * (len(word) - 2) + word[-1]
      else:
         return '*' * len(word)


   result = re.sub(pattern, replace_match, value, flags=re.IGNORECASE)

   return mark_safe(result)