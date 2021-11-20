[Главная](https://ceammc.github.io/pd-help/) 
---

# {{info["name"]|striptags}}

##### Версия {{info["version"]}}

{{info["descr"]}}

## категории

{% for cat in data %}
### [{{cat["name"]}}](category_{{cat["name"]|urlencode}}.html)
{% if cat["info"] %}###### {{cat["info"]|trim}}{% endif %}
---

{% for obj in cat["objects"] %}
[**{{obj["name"]}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]}} 
{% endfor %}
{% endfor %}

---
**Сайт:** [{{info["website"]}}]({{info["website"]}})

**Лицензия:** {{info["license"]}}

**Авторы:** {{info["authors"]|map(attribute="text")|join(', ')}}
