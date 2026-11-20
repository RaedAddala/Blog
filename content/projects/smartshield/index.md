---
title: "SmartShield: AI-Powered Network Intrusion Detection"
date: 2024-12-01
description: "Network intrusion detection and incident reporting: packet capture over RabbitMQ, Zeek and Argus feature extraction, two-stage CatBoost detection and classification, a NestJS/React dashboard, and CrewAI-generated incident reports."
summary: "AI-driven network intrusion detection: pcaps shipped over RabbitMQ, flow features extracted with Zeek and Argus, two-stage CatBoost detection and attack classification (F1 91.5% on UNSW-NB15), a NestJS/React dashboard, and LLM agents that write incident reports."
tags: ["Intrusion Detection", "Machine Learning", "CatBoost", "LLM", "CrewAI", "Zeek", "RabbitMQ", "FastAPI", "NestJS", "React", "Go", "Docker"]
categories: ["Projects"]
keywords: ["SmartShield", "network intrusion detection", "UNSW-NB15", "CatBoost", "Zeek", "Argus", "RabbitMQ", "CrewAI", "incident response", "TSYP", "IEEE Computer Society"]
role: "Team member (8-person team)"
status: "Completed · 2nd place, IEEE Computer Society Challenge (TSYP '12)"
period: "September to December 2024"
weight: 15
repo: "https://github.com/Smartshield-INSAT"
demo: ""
comments: false
---

SmartShield is an AI-driven platform for detecting network attacks and helping analysts respond to them. It watches network traffic, classifies malicious flows with machine learning, and generates readable incident reports with LLM agents. We built it as an eight-person team at INSAT, with support from the IEEE INSAT Student Branch Computer Society, for the IEEE Computer Society Challenge at the TSYP '12 congress.

Links: [GitHub organization](https://github.com/Smartshield-INSAT) · [technical paper](https://github.com/Smartshield-INSAT/Technical-Paper/blob/main/SMARTSHIELDTechPaper.pdf) (PDF) · [demo video](https://youtu.be/2Nd6C_SpXak)

## The problem

Classic security monitoring (SIEM) relies mostly on hand-written rules. The paper identifies three gaps it set out to close: **latency and scalability** when processing traffic, **explainability** of why something was flagged, and **reporting** that turns detections into something an analyst can act on.

A key design choice was where detection runs. Agents on every monitored machine are exposed to local tampering and log poisoning. Cloud-based detection brings a larger attack surface, external dependencies, latency, and costs beyond a reasonable budget. SmartShield is instead a **spectator**: it is not part of the systems it watches, but monitors their network traffic from separate infrastructure, which makes it harder to attack and more reliable.

## Architecture

The platform is a set of containerized services, each in its own repository, connected by a message queue and HTTP APIs:

1. **Capture agent (Go).** Runs tcpdump, rotates the capture into a new pcap file every 5 seconds, and publishes each file to **RabbitMQ** with the ID of the device it came from. The queue decouples capture from processing.
2. **Flow feature extraction.** A processor consumes the queue and runs each pcap through **Zeek** and **Argus**. Argus produces per-flow statistics (duration, bytes and packets per direction, load, jitter, inter-packet times, TCP round-trip time), Zeek scripts add protocol-level features such as HTTP transaction depth and FTP logins, and a few connection-count features are computed in Python. The outputs are joined per flow into the feature set of the UNSW-NB15 dataset, so the live traffic matches what the models were trained on.
3. **ML engine (FastAPI).** Serves the models: a flow first goes through a binary **detection** model (attack or normal), then a **classification** model assigns the attack category (Generic, Reconnaissance, Fuzzers, Exploits, or DoS). Flows flagged as threats are sent to the backend.
4. **Backend (NestJS).** Stores flow records and their labels in **PostgreSQL**, keeps the mapping between monitored servers and devices in **Redis**, and exposes aggregation APIs: traffic over time, attack categories, the most-targeted servers, and recent offenses.
5. **Dashboard (React).** Charts traffic and attack categories, lists offenses, manages monitored devices, and embeds **Kibana** for packet-level statistics that the processor indexes in **Elasticsearch**. It refreshes from the backend every 14 seconds.
6. **Report generator (CrewAI).** On demand from an offense, three LLM agents work in sequence: a **threat analyzer** explains the attack, a **mitigation strategist** proposes countermeasures, and a **report generator** writes them up. The result is returned as a PDF. The LLMs are served through Groq.

## Detection models

The models are trained on **UNSW-NB15**. The team also evaluated CIC-IDS2017 and chose UNSW-NB15 for the final system. Preprocessing groups rare protocol, service, and state values, applies log transforms to skewed features, removes highly correlated features, and adds engineered ratio features.

The team benchmarked XGBoost, CatBoost, LightGBM, a neural network, and TabNet. The gradient-boosted trees led (weighted F1 around 0.87 before tuning, against 0.78 to 0.81 for the neural models), and **CatBoost** was chosen for its native handling of categorical features and its ordered boosting, then tuned with Optuna.

Results reported in the paper for the tuned detection model:

| Metric | Detection model |
|---|---|
| Precision | 88.97% |
| Recall | 94.26% |
| F1-score | 91.5% |
| ROC AUC | about 0.98 |

The paper describes tuning toward recall, to catch as many intrusion attempts as possible. The attack-category classifier reaches a weighted F1 of about 0.84 across the five categories: it is strongest on Generic attacks and weakest on DoS. The model API answers in **0.4 to 0.8 seconds per request**.

## Tech stack

- **Capture and messaging:** Go, tcpdump, RabbitMQ
- **Traffic analysis:** Zeek, Argus, pyshark, Elasticsearch, Kibana
- **Machine learning:** Python, CatBoost, scikit-learn, pandas, Optuna, FastAPI
- **LLM reporting:** CrewAI, LangChain, Groq
- **Backend and dashboard:** NestJS (Nx monorepo), TypeORM, PostgreSQL, Redis, React, Tailwind CSS, Chart.js, Recharts
- **Infrastructure:** Docker, Docker Compose

## Limitations and next steps

The paper lists the dependence on specific training datasets as the main limitation, and points to adaptive learning on live traffic, closer interaction with human analysts, and more explainable-AI components as next steps.
