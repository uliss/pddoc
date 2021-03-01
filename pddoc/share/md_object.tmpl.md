[< reference home](index.html)
---

# ${title | h}


${description|h}

---

${info|h}<br>


---


![example](examples/${title}-example.jpg)

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
[![${obj['name']|h}](${obj['image']|h})](${obj['name']}.html)
% endfor
% endif
