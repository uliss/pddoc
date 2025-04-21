---
layout: default_ru
---
[index](../index.html)
---

# Методы:

{%- for m, objs in data.items()|sort() %}
### {{m}}

{%- for x in objs|sort() %}
[{{x}}]({{x|urlencode}}.html)
{%- endfor %}
{% endfor %}

---
**Сайт:** [{{info["website"]}}]({{info["website"]}})

**Лицензия:** {{info["license"]}}

**Авторы:** {{info["authors"]|map(attribute="text")|join(', ')}}
