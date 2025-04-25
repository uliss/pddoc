[index](index.html) :: [{{category}}](category_{{category|urlencode}}.html)
---

# {{title|ws}}

{%- if aliases %}
**aliases:** {{aliases|join(", ")|ws|replace('~','\~')}}
{% endif %}

###### {{description|ws}}

{% if since %}*available since version:* {{since}}{% endif %}

---

{% if info %}
## information
{{info|ws|escape}}
{%- endif %}

{% if example_pd_dir %}
[![example]({{example_img_dir}}{{title|urlencode}}.jpg)]({{example_pd_dir}}{{title|urlencode}}.pd)
{% else %}
![example]({{example_img_dir}}{{title|urlencode}}.jpg)
{% endif %}

{% if arguments %}
## arguments:
{% for arg in arguments %}
* **{{arg.name()|trim}}**
{{arg.text()|ws|wordwrap}}<br>
{%- if arg.type() %}
_type:_ {{arg.type()}}<br>
{%- endif %}
{%- if arg.units() %}
_units:_ {{arg.units()|join(', ')}}<br>
{%- endif %}
{% endfor -%}
{% endif %}

{% if methods %}
## methods:
{% for m in methods %}
* **{{m.name()|trim}}**
{{m.text()|ws|wordwrap}}<br>
{% if m.items() %}  __parameters:__{% endif %}
{%- for param in m.items() %}
  - **{{param.param_name()}}** {{param.text()|ws}}<br>
{%- if param.type() %}
    type: {{param.type()}} <br>
{%- endif %}
{%- if param.units() %}
    units: {{param.units()|join(', ')}} <br> 
{%- endif %}
{%- if param.required() %}
    required: {{param.required()}} <br> 
{%- endif %}
{% endfor -%}
{% endfor %}
{% endif %}

{% if properties %}
## properties:
{% for prop in properties %}
* **{{prop.name()|trim}}** {% if prop.access() != 'readwrite' %}({{prop.access()}}){% endif %}
{% if prop.access() == 'readonly' %}Get {% else %}Get/set {% endif -%}
{{prop.text()|ws|wordwrap}}<br>
{%- if prop.type() %}
_type:_ {{prop.type()}}<br>
{%- endif %}
{%- if prop.units() %}
_units:_ {{prop.units()|join(', ')}}<br>
{%- endif %}
{%- if prop.enum() %}
_enum:_ {{prop.enum()|join(', ')}}<br>
{%- endif %}
{%- if prop.range()|length == 2 and prop.range()[0] and prop.range()[1] %}
_range:_ {{prop.range()|join('..')}}<br>
{%- elif prop.min() %}
_min value:_ {{prop.min()}}<br>
{%- elif prop.max() %}
_max value:_ {{prop.max()}}<br>
{%- endif %}
{%- if prop.default() %}
_default:_ {{prop.default()}}<br>
{%- endif %}
{% endfor -%}
{% endif %}

{% if inlets %}
## inlets:
{% for x in inlets %}
{%- if x.items() %}
* {{x.items()[0].text()|ws}}<br>
{%- endif %}
_type:_ {{x.type()}}
{%- endfor %}
{% endif %}

{% if outlets %}
## outlets:
{% for x in outlets %}
* {{x.text()|ws}}<br>
_type:_ {{x.type()}}
{%- endfor %}
{% endif %}

{% if keywords %}
## keywords:
{% for k in keywords %}
[{{k}}](keywords/{{k|urlencode}}.html)
{%- endfor %}
{% endif %}

{% if see_also %}
**See also:**
{%- for obj in see_also %}
[\[{{obj['name']}}\]]({{obj['name']|urlencode}}.html)
{%- endfor %}
{% endif %}

{% if version %}**Version:** {{version}}{% endif %}

{% if authors %}**Authors:** {{authors|join(", ")}}{% endif %}

{% if license and license['url'] %}
**License:** 
[![{{license['name']}}]({{license['url']}})]({{license['url']}})
{% endif %}

{% if license and not license['url'] %}
**License:** {{license['name']}}
{% endif %}

{% if website %}**Website:** [![{{website}}]({{website}})]({{website}}){% endif %}

{% if contacts %}**Contacts:** [![{{contacts}}](mailto:{{contacts}})](mailto:{{contacts}}){% endif %}

