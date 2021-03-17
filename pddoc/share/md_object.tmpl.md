[< reference home](index.html)
---

# {{title|striptags}}

{{description}}

{{author}}

---

${info|h}<br>


---


![example](examples/{{title}}-example.jpg)

{% if arguments %}
### arguments:

{% for obj in arguments %}
{{obj.main_info_prefix()}}<br>
{% endfor %}
{% endif %}oc

### properties:

{% for prop in properties %}
**{{prop.main_info_prefix()}}{% if prop.readonly() %}(readonly){% endif %}** 
{% if prop.readonly() %}Get {% else %}Get/set {% endif -%}
{{prop.text()|striptags|wordwrap}}
{%- if prop.type_info() %}
__type:__ {{prop.type_info()}}
{%- endif %}
{%- if prop.enum() %}
__enum:__ {{prop.enum()|join(', ')}}
{%- endif %}
{%- if prop.range()|length == 2 %}
__range:__ {{prop.range()|join('..')}}
{%- elif prop.min() %}
__min value:__ {{prop.min()}}
{%- elif prop.max() %}
__max value:__ {{prop.max()}}
{%- endif %}
{% endfor %}

{% if see_also %}
### see also:
{% for obj in see_also %}
[![{{obj['name']}}]({{obj['image']|urlencode}})]({{obj['name']|urlencode}}.html)
{%- endfor %}
{% endif %}
