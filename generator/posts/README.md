# Blog articles

One file per article: `posts/<url-slug>.md`. The site builds a page at `/blog/<url-slug>/`.

```
---
title: The H1 shown on the page
seo: The <title> tag, max ~60 characters | Artlify
description: Meta description, 140-160 characters.
slug: url-slug
category: hiring-an-agency | social-media | meta-ads | funnels-automation
date: 2026-11-15
updated: 2026-11-15
excerpt: One line shown on blog cards.
quick: 40-60 word direct answer to the main question (shown in the Quick answer box).
pillar: yes        # only for the main guide of a category
draft: yes         # optional: hides the article
---

Article body in markdown: ## for sections, ### for subsections, lists, tables, links like [text](/services/paid-ads/).

## Frequently asked questions

### Question one?
Answer in 40-70 words.
```

The FAQ section becomes an accordion with FAQPage schema. The read time, table of contents, breadcrumbs, author box, related posts, sitemap, RSS feed and llms.txt are generated automatically.
