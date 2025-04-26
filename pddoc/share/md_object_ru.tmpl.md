---
layout: default_ru
---
[index](index.html) :: [{{category}}](category_{{category|urlencode}}.html)
---

# {{title|ws}}

###### {{description|ws|replace('[','\\[')|replace(']','\\]')}}

{% if since %}*доступно с версии:* {{since}}{% endif %}

---

{% if info %}
## информация
{{info|ws}}
{%- endif %}

{% if example_pd_dir %}
[![example]({{example_img_dir}}{{title|urlencode}}.jpg)]({{example_pd_dir}}{{title|urlencode}}.pd)
{% else %}
![example]({{example_img_dir}}{{title|urlencode}}.jpg)
{% endif %}

{% if arguments %}
## аргументы:
{% for arg in arguments %}
* **{{arg.name()|trim}}**
{{arg.text()|ws|wordwrap}}<br>
{%- if arg.type() %}
_тип:_ {{arg.type()}}<br>
{%- endif %}
{%- if arg.units() %}
_единица:_ {{arg.units()|join(', ')}}<br>
{%- endif %}
{% endfor -%}
{% endif %}

{% if methods %}
## методы:
{% for m in methods %}
* **{{m.name()|trim}}**
{{m.text()|ws|wordwrap}}<br>
{% if m.items() %}  __параметры:__{% endif %}
{%- for param in m.items() %}
  - **{{param.param_name()}}** {{param.text()|ws}}<br>
{%- if param.type() %}
    тип: {{param.type()}} <br>
{%- endif %}
{%- if param.units() %}
    единица: {{param.units()|join(', ')}} <br> 
{%- endif %}
{%- if param.required() %}
    обязательно: {{param.required()}} <br> 
{%- endif %}
{% endfor -%}
{% endfor %}
{% endif %}

{% if properties %}
## свойства:
{% for prop in properties %}
* **{{prop.name()|trim}}** {% if prop.access() != 'readwrite' %}({{prop.access()}}){% endif %}
{% if prop.access() == 'readonly' %}Запросить {% else %}Запросить/установить {% endif -%}
{{prop.text()|ws|wordwrap}}<br>
{%- if prop.type() %}
_тип:_ {{prop.type()}}<br>
{%- endif %}
{%- if prop.units() %}
_единица:_ {{prop.units()|join(', ')}}<br>
{%- endif %}
{%- if prop.enum() %}
_варианты:_ {{prop.enum()|join(', ')}}<br>
{%- endif %}
{%- if prop.range()|length == 2 and prop.range()[0] and prop.range()[1] %}
_диапазон:_ {{prop.range()|join('..')}}<br>
{%- elif prop.min() %}
_минимальное значение:_ {{prop.min()}}<br>
{%- elif prop.max() %}
_максимальное значение:_ {{prop.max()}}<br>
{%- endif %}
{%- if prop.default() %}
_по умолчанию:_ {{prop.default()}}<br>
{%- endif %}
{% endfor -%}
{% endif %}

{% if inlets %}
## входы:
{% for x in inlets %}
{%- if x.items() %}
* {{x.items()[0].text()|ws}}<br>
{%- endif %}
_тип:_ {{x.type()}}
{%- endfor %}
{% endif %}

{% if outlets %}
## выходы:
{% for x in outlets %}
* {{x.text()|ws}}<br>
_тип:_ {{x.type()}}
{%- endfor %}
{% endif %}

{% if keywords %}
## ключевые слова:
{% for k in keywords %}
[{{k}}](keywords/{{k|urlencode}}.html)
{%- endfor %}
{% endif %}

{% if see_also %}
**Смотрите также:**
{%- for obj in see_also %}
[\[{{obj['name']}}\]]({{obj['name']|urlencode}}.html)
{%- endfor %}
{% endif %}

{% if version %}**Версия:** {{version}}{% endif %}

{% if authors %}**Авторы:** {{authors|join(', ')}}{% endif %}

{% if license and license['url'] %}
**Лицензия:** 
[![{{license['name']}}]({{license['url']}})]({{license['url']}})
{% endif %}

{% if license and not license['url'] %}
**Лицензия:** {{license['name']}}
{% endif %}

{% if website %}**Website:** [![{{website}}]({{website}})]({{website}}){% endif %}

{% if contacts %}**Контакты:** [![{{contacts}}](mailto:{{contacts}})](mailto:{{contacts}}){% endif %}

