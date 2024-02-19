---
layout: default
---

# Hey Traveller

When solving problems, dig at the roots instead of just hacking at the leaves.

# Posts

{% for post in site.posts %}
- [{{ post.title }}]({{ post.url }})
{% endfor %}
