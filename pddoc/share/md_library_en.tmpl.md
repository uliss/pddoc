[Home](https://ceammc.github.io/pd-help/) 
---

# {{info["name"]|striptags}}

##### Version {{info["version"]}}

{{info["descr"]}}

## categories

{%- for cat in data %}
[{{cat["name"]}}](#cat_{{cat["name"]}})
{%- endfor %}

{% for cat in data %}
### <a id="cat_{{cat["name"]}}" href="category_{{cat["name"]|urlencode}}.html">{{cat["name"]}}</a>
{% if cat["info"] %}{{cat["info"]|trim}}{% endif %}

---

{% for obj in cat["objects"] %}
[**{{obj["name"]|replace('~','\\~')}}**]({{obj["name"]|urlencode}}.html): {{obj["descr"]|replace('[','\\[')|replace(']','\\]')}} 
{% endfor %}
{% endfor %}

---
**Keywords:**
{%- for k in keywords.keys()|sort() %}
[{{k}}](keywords/{{k|urlencode}}.html)
{%- endfor %}

---
**Website:** [{{info["website"]}}]({{info["website"]}})

**License:** {{info["license"]}}

**Authors:** {{info["authors"]|map(attribute="text")|join(', ')}}
