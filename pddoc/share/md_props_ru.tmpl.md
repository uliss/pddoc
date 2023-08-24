[index](../index.html)
---

# Свойства:

{%- for p, objs in data.items()|sort() %}
### {{p}}

{%- for x in objs|sort() %}
[{{x}}]({{x|urlencode}}.html)
{%- endfor %}
{% endfor %}

---
**Сайт:** [{{info["website"]}}]({{info["website"]}})

**Лицензия:** {{info["license"]}}

**Авторы:** {{info["authors"]|map(attribute="text")|join(', ')}}
