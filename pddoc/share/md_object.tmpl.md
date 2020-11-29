[<<< reference home](ceammc_lib.md)
---

# ${title | h}

```
${pd_ascii}
```
---
${description|h}
---
arguments:

% for obj in arguments:
${obj.main_info()|h}<br>
% endfor

---
properties:

% for obj in properties:
${obj.main_info()|h}<br>
% endfor

% if see_also:
---
see also:<br>
% for obj in see_also:
[![${obj['name']|h}](${obj['image']|h})](${obj['name']}.md)
% endfor
% endif
