[index](../index.html)
---

## Ключевое слово: {{key}}

### Объекты:

{%- for x in obj %}
* [{{x}}](../{{x}}.html)
{%- endfor %}

---
**Сайт:** [{{info["website"]}}]({{info["website"]}})

**Лицензия:** {{info["license"]}}

**Авторы:** {{info["authors"]|map(attribute="text")|join(', ')}}
