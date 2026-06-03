---
title: "What I Learned Building a Kafka Streaming Pipeline"
date: 2026-06-02
draft: false
description: "Lessons from designing, debugging, and documenting a Kafka-based streaming project."
summary: "Notes on Kafka topics, event design, Docker Compose, reliability, and documenting a streaming project for a portfolio."
author: "Raed Addala"
keywords: ["Kafka", "streaming pipeline", "backend", "distributed systems", "Docker"]
tags: ["kafka", "distributed-systems", "backend", "docker", "learning"]
categories: ["Project Writeups"]
series: ["Backend Learning"]
images: ["/images/projects/kafka-pipeline.jpg"]
cover:
  image: "/images/projects/kafka-pipeline.jpg"
  alt: "Kafka streaming pipeline architecture"
ShowToc: true
TocOpen: false
comments: true
---

Building a Kafka project forced me to think beyond endpoints and database tables. The core question became: what happened, who needs to know, and what should happen if processing fails?

## Event Design Matters

Good event names and payloads make the system easier to reason about. A vague event becomes expensive later because every consumer has to guess what it means.

## Local Environments Should Be Repeatable

Docker Compose made the project much easier to test and explain. A reviewer should be able to start the system without guessing which services are required.

## Reliability Is a Design Topic

Retries, idempotency, ordering, and duplicate messages are not edge details. They are central parts of event-driven systems.

## Documentation Improves the Project

Writing the case study made weak assumptions visible. If I could not explain a design choice clearly, I needed to revisit it.
