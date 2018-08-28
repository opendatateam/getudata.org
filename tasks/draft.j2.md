---
title: {{ title }}
date: {{ date.strftime('%Y-%m-%d %H:%M') }}
modified: {{ date.strftime('%Y-%m-%d %H:%M') }}
image: https://placehold.it/1920x1080
tags:{% for tag in tags %}
  - {{ tag|trim }}
  {%- endfor %}
slug: {{ slug }}
lang: en
{% if category -%}
category: {{ category }}
{% endif -%}
authors: Open Data Team
summary: {{ summary }}
{% if is_article -%}
status: draft
{% endif -%}
---
