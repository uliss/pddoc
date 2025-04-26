[index](index.html) 
---

# Category: {{cat["name"]|striptags}}

{{cat["descr"]}}

{% for obj in cat["objects"] %}
[**{{obj["name"]|escape|replace('~','\\~')}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]|replace('[','\\[')|replace(']','\\]')}} {% if obj["aliases"] %}<br>
_aliases:_ {{obj["aliases"]|join(", ")|replace('~','\\~')}}
{% endif %}
{% endfor %}

**Version:** {{info["version"]}}

**License:** {{info["license"]}}
