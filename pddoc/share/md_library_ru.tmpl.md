---
layout: default_ru
---
[Главная](https://ceammc.github.io/pd-help/) 
---

# {{info["name"]|striptags}}

##### Версия {{info["version"]}}

{{info["descr"]}}

## категории

{%- for cat in data %}
[{{cat["name"]}}](#cat_{{cat["name"]}})
{%- endfor %}

{% for cat in data %}
### <a id="cat_{{cat["name"]}}" href="category_{{cat["name"]|urlencode}}.html">{{cat["name"]}}</a>
{% if cat["info"] %}{{cat["info"]|trim}}{% endif %}
---

{% for obj in cat["objects"] %}
[**{{obj["name"]}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]}} 
{% endfor %}
{% endfor %}

---
**Сайт:** [{{info["website"]}}]({{info["website"]}})

**Лицензия:** {{info["license"]}}

**Авторы:** {{info["authors"]|map(attribute="text")|join(', ')}}
