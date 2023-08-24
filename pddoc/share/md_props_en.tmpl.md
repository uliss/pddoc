[index](../index.html)
---

# Properties:

{%- for p, objs in data.items()|sort() %}
### {{p}}

{%- for x in objs|sort() %}
[{{x}}]({{x|urlencode}}.html)
{%- endfor %}
{% endfor %}

---
**Website:** [{{info["website"]}}]({{info["website"]}})

**License:** {{info["license"]}}

**Authors:** {{info["authors"]|map(attribute="text")|join(', ')}}
