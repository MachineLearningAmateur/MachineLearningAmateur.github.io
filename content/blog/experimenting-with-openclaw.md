---
title: Experimenting with OpenClaw
slug: experimenting-with-openclaw
date: '2026-05-28'
summary: A brief summary of my experience with OpenClaw
type: blog
---

In the past few days, I've been experimenting with OpenClaw. You may be wondering what OpenClaw is. Well, it's an agentic harness that allows you to schedule daily tasks to run each day and give agents a personality as well. Since this is an agentic harness, it still requires you to be subscribed to a LLM service (ChatGpt, Claude, DeepSeek, etc.). For my personal use, I am currently using Codex from ChatGPT Plus ($20 monthly plan) and DeepSeek for API calls when ChatGpt usage limits are reached. However, it is possible to also use a local LLM to run OpenClaw, but this would require a more powerful machine which is currently out of my budget at the moment. Maybe in the future, I may invest in a Mac Studio M4 128GB ($3k-$4k) to host a local LLM for OpenClaw😆.

I currently have OpenClaw installed on an old laptop to run locally. There are a few reasons why I am using an old laptop instead of my personal computer. The first reason for using an old laptop is because I want to let the agents that I create run freely on the machine without any concerns of potentially wiping or corrupting the data on the machine. Alternatively, I did consider hosting OpenClaw on a VPS (virtual private server), but I decided to opt out of doing that because I read about the concerns of potential security breaches due to online exposure which led to the leakage of API keys and exposing private data (such as personal emails). 

Anyway, enough background info about OpenClaw. So what have I been using OpenClaw for? I had OpenClaw open a gateway with Discord as my primary mode of communication with the agents. Originally, I was using Telegram as the central chat interface to talk to the agents since it was easier to set up. However, after doing a bit of investigation, I decided to go with Discord because it allowed me to create multiple channels with each channel dedicated to an agent with its own expertise and personality. These agents are defined by their respective markdown files such as Memory.md, Soul.md, Identity.md, and etc. I basically created agents for specific tasks such as an agent that acts as my wealth advisor and does research on the stock market, and another agent that does research on agentic research papers to learn and self-evolve itself and other fellow agents via skill enhancements and personality updates. It's just fascinating how I can have  my personal agentic ecosystem that is able to grow without me getting involved after the initial setup. 

Needless to say, I had a lot of fun experimenting with OpenClaw and ended up blowing through my weekly Codex limit within a few days 😅. This is why I had to buy some tokens from DeepSeek and use their API service as a fallback model to allow my agents to continue "breathing". I look forward to the growth of my agents and plan on adding additional agents as I see fit based on my needs. 

If you haven't already, definitely give OpenClaw a try at: https://openclaw.ai/
