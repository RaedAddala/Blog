---
title: "Neon"
date: 2024-06-04
description: "A microservice live-streaming platform built with Elixir/Phoenix, SvelteKit, Kong, and a Membrane RTMP-to-HLS pipeline."
summary: "A Twitch-like live-streaming platform for software and IT streamers, built around Elixir/Phoenix microservices, SvelteKit, Kong, PostgreSQL, WebSocket chat, and RTMP-to-HLS media processing."
tags: ["Elixir", "Phoenix", "Membrane", "SvelteKit", "Kong", "Docker", "PostgreSQL", "RTMP", "HLS", "Microservices", "Live Streaming"]
categories: ["Projects"]
keywords: ["Neon live streaming platform", "Elixir streaming platform", "Membrane RTMP HLS", "SvelteKit microservices", "Kong API gateway"]
tech: ["Elixir", "Phoenix", "Membrane", "SvelteKit", "Kong", "Docker", "Docker Compose", "PostgreSQL", "RTMP", "HLS", "WebSocket"]
role: "Software engineering project contributor"
status: "Completed"
featured: true
weight: 10
repo: "https://github.com/RaedAddala/Neon"
demo: ""
images: ["/images/projects/neon-cover.png"]
cover:
  image: "/images/projects/neon-cover.png"
  alt: "Abstract live streaming infrastructure cover for Neon"
comments: false
---

Neon is a live-streaming platform designed for software engineering and IT streamers. It explores the architecture behind a Twitch-like system: users can authenticate, manage profiles, start or watch streams, and interact through real-time chat while the backend handles media ingestion and browser-ready distribution.

The project was built with [Zeineb BenAbdallah](https://github.com/zei-ZZ) and [Mohamed Hedi Ben Ali](https://github.com/medhedibenali) as a software engineering academic project at INSAT. The code is available on [GitHub](https://github.com/RaedAddala/Neon).

## Architecture

Neon uses a microservice architecture instead of placing authentication, chat, and streaming logic in one application. The backend is split into three Phoenix services:

- **Authentication service** for registration, login, profile management, PostgreSQL persistence, and JWT issuance.
- **Live chat service** for low-latency viewer interaction through Phoenix Channels and WebSocket connections.
- **Live streaming service** for receiving an RTMP stream, processing it with Membrane, and exposing HLS output to viewers.

Each service is containerized with Docker and wired together with Docker Compose. Kong sits in front of the services as the API gateway, giving the platform one routing layer for HTTP APIs, uploaded assets, chat traffic, and stream watching routes. This keeps the service boundaries visible while still giving the frontend one stable entry point.

## Gateway and Authorization

Kong acts as the middleware layer between the SvelteKit frontend and the backend services. It routes public authentication requests, protects profile-changing endpoints, forwards live chat traffic, and exposes the stream watching path.

The authentication design uses JWTs signed by the auth service and verified at the gateway. A custom Kong auth plugin handles the cases where a browser WebSocket handshake cannot send arbitrary authorization headers: for chat routes, tokens can be read from query parameters and converted into request data that the downstream service can use. That keeps authorization close to the gateway without forcing every service to duplicate the same token verification logic.

## Streaming Pipeline

The streaming service uses Membrane to model multimedia processing as a pipeline. A streamer sends video from an encoder such as OBS over RTMP. The service demuxes the incoming FLV stream, separates audio and video, parses AAC and H.264, packages the tracks as fragmented MP4 segments, and writes HLS output for browser playback.

![Neon RTMP to HLS pipeline](/images/projects/neon-architecture.png)

This split matches the practical difference between first-mile and last-mile delivery. RTMP is useful for reliable, low-latency ingestion from the streamer, while HLS is easier to distribute to viewers through standard HTTP-based playback.

## Frontend

The frontend is a SvelteKit application with routes for signup, login, profile management, starting a stream, and watching another user's stream. The watch page combines the video player and live chat, while the stream page exposes controls to start and stop a broadcast.

SvelteKit was chosen for a small, fast frontend with straightforward routing and component structure. Tailwind CSS handles the interface styling, while typed stores and utility wrappers keep client-side state and API calls organized.

## Engineering Takeaways

The main engineering challenge was deciding where responsibilities belong in a distributed streaming platform. Authentication, chat, and media processing have different scaling and failure characteristics, so separating them made the system easier to reason about and gave Kong a clear role as the shared entry point.

The project also made the protocol tradeoffs concrete. RTMP, HLS, WebSocket, JWT authorization, and HTTP gateway routing each solve a different part of the platform. Bringing them together required thinking beyond individual frameworks and focusing on end-to-end data flow: how a stream enters the system, how it becomes playable in the browser, and how viewer interaction stays real-time beside it.
