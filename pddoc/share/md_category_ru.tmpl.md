[index](index.html) 
---

# {{cat["name"]|striptags}}

{{cat["descr"]}}

{% for obj in cat["objects"] %}
[**{{obj["name"]}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]}} {% if obj["aliases"] %}<br>
_псевдонимы:_ {{obj["aliases"]|join(", ")}}
{% endif %}
{% endfor %}

**Версия:** {{info["version"]}}

**Лицензия:** {{info["license"]}}
