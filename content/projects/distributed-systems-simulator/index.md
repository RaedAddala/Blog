---
title: "Distributed Systems Simulator"
date: 2026-06-02
description: "A learning-oriented simulator for visualizing distributed systems concepts such as coordination, latency, failures, and consistency."
summary: "A project case study focused on making distributed systems behavior easier to reason about through simulation."
keywords: ["distributed systems project", "systems design", "simulation", "software engineering portfolio"]
tags: ["distributed-systems", "simulation", "systems-design"]
categories: ["Projects"]
tech: ["Python", "JavaScript", "Docker", "Markdown"]
role: "Systems modeling and documentation"
status: "Prototype"
featured: true
weight: 20
repo: "https://github.com/RaedAddala"
github: "https://github.com/RaedAddala"
demo: ""
images: ["/images/projects/distributed-systems-simulator.jpg"]
cover:
  image: "/images/projects/distributed-systems-simulator.jpg"
  alt: "Distributed systems simulator interface"
comments: false
sitemap:
  priority: 0.8
  changefreq: "monthly"
---

## Problem

Distributed systems concepts can feel abstract until failures, delay, retries, and partial state are made visible. This project is designed as a learning tool for exploring those behaviors.

## Solution

The simulator models nodes, messages, delays, and failure events. The project writeup focuses on how small implementation choices affect consistency and system behavior.

## Implementation Highlights

- Modeled message delivery with configurable delay.
- Used simple scenarios to explain coordination and failure handling.
- Kept the interface and documentation focused on learning rather than visual complexity.

## Lessons Learned

The biggest value of a simulator is not perfect realism. It is the ability to isolate one systems idea at a time and make the consequences visible.
