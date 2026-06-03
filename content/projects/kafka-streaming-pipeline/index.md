---
title: "Kafka Streaming Pipeline"
date: 2026-06-02
description: "A real-time data pipeline project using Kafka, backend services, Docker, and observability-oriented design."
summary: "A case study for a Kafka-based streaming pipeline focused on event ingestion, processing, persistence, and operational visibility."
keywords: ["Kafka project", "streaming pipeline", "backend engineering", "distributed systems"]
tags: ["kafka", "backend", "distributed-systems", "docker"]
categories: ["Projects"]
tech: ["Kafka", "Java", "Docker", "PostgreSQL", "Prometheus"]
role: "Backend and data pipeline design"
status: "Case study"
featured: true
weight: 10
repo: "https://github.com/RaedAddala"
github: "https://github.com/RaedAddala"
demo: ""
images: ["/images/projects/kafka-pipeline.jpg"]
cover:
  image: "/images/projects/kafka-pipeline.jpg"
  alt: "Kafka streaming pipeline architecture"
comments: false
sitemap:
  priority: 0.8
  changefreq: "monthly"
---

## Problem

This project explores how to move from a simple request-response backend mindset to an event-driven architecture where services publish, process, and persist streams of data.

## Constraints

The goal was to keep the project understandable for a student portfolio while still showing production-aware thinking: message durability, failure modes, logging, retry behavior, and clear documentation.

## Solution

The pipeline is organized around producers, Kafka topics, stream-processing services, and a persistence layer. Docker Compose keeps the environment repeatable, while the documentation explains what each service owns and how events flow through the system.

## Implementation Highlights

- Designed topic boundaries around clear event types.
- Used Docker Compose to make local testing reproducible.
- Documented the pipeline architecture so reviewers can understand the system quickly.
- Tracked lessons about retries, idempotency, and observability.

## Lessons Learned

Kafka projects are most useful in a portfolio when the writeup explains tradeoffs instead of only listing tools. The most important details are usually where data can be duplicated, lost, delayed, or processed out of order.
