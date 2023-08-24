[index](../index.html)
---

## Keyword: {{key}}

### Objects:

{%- for x in obj %}
* [{{x}}](../{{x}}.html)
{%- endfor %}

---
**Website:** [{{info["website"]}}]({{info["website"]}})

**License:** {{info["license"]}}

**Authors:** {{info["authors"]|map(attribute="text")|join(', ')}}
