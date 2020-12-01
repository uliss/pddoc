[< справка — содержание](ceammc_lib.html)
---

# ${title | h}


${description|h}

---

${info|h}<br>


---


```
${pd_ascii}
```

---
аргументы:

% for obj in arguments:
${obj.main_info()|h}<br>
% endfor

---
свойства:

% for obj in properties:
${obj.main_info()|h}<br>
% endfor

% if see_also:
---
смотрите также:<br>
% for obj in see_also:
[![${obj['name']|h}](${obj['image']|h})](${obj['name']}.html)
% endfor
% endif
