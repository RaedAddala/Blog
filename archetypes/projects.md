---
# Create projects as folders so images sit next to the page:
#   hugo new content projects/<name>/index.md   then add cover.jpg to that folder.
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
description: ""
summary: ""
tags: []
categories: ["Projects"]
keywords: []
role: ""
status: "In progress"
period: ""
weight: 50
repo: ""
demo: ""
images: ["cover.jpg"]
cover:
  image: "cover.jpg"
  relative: true
  alt: ""
comments: false
---
