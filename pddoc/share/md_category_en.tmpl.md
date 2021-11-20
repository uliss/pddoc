[index](index.html) 
---

# {{cat["name"]|striptags}}

{{cat["descr"]}}

{% for obj in cat["objects"] %}
[**{{obj["name"]}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]}} {% if obj["aliases"] %}<br>
_aliases:_ {{obj["aliases"]|join(", ")}}
{% endif %}
{% endfor %}

**Version:** {{info["version"]}}

**License:** {{info["license"]}}
