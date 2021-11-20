[Home](https://ceammc.github.io/pd-help/) 
---

# {{info["name"]|striptags}}

##### Version {{info["version"]}}

{{info["descr"]}}

## categories

{% for cat in data %}
### [{{cat["name"]}}](category_{{cat["name"]|urlencode}}.html)
{% if cat["info"] %}###### {{cat["info"]|trim}}{% endif %}
---

{% for obj in cat["objects"] %}
[**{{obj["name"]|replace('~','\~')}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]}} 
{% endfor %}
{% endfor %}

---
**Website:** [{{info["website"]}}]({{info["website"]}})

**License:** {{info["license"]}}

**Authors:** {{info["authors"]|map(attribute="text")|join(', ')}}
