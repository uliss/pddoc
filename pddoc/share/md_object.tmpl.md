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
**{{prop.name()|trim}}** {% if prop.readonly() %}(readonly){% endif %}
{% if prop.readonly() %}Get {% else %}Get/set {% endif -%}
{{prop.text()|striptags|wordwrap}}<br>
{%- if prop.type() %}
__type:__ {{prop.type()}}<br>
{%- endif %}
{%- if prop.units() %}
__units:__ {{prop.units()}}<br>
{%- endif %}
{%- if prop.enum() %}
__enum:__ {{prop.enum()|join(', ')}}<br>
{%- endif %}
{%- if prop.range()|length == 2 and prop.range()[0] and prop.range()[1] %}
__range:__ {{prop.range()|join('..')}}<br>
{%- elif prop.min() %}
__min value:__ {{prop.min()}}<br>
{%- elif prop.max() %}
__max value:__ {{prop.max()}}<br>
{%- endif %}
{%- if prop.default() %}
__default:__ {{prop.default()}}<br>
{%- endif %}
{% endfor %}

{% if see_also %}
### see also:
{% for obj in see_also %}
[![{{obj['name']}}]({{obj['image']|urlencode}})]({{obj['name']|urlencode}}.html)
{%- endfor %}
{% endif %}
