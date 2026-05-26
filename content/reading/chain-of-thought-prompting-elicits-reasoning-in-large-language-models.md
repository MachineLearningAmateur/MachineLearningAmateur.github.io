---
title: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
slug: chain-of-thought-prompting-elicits-reasoning-in-large-language-models
date: '2026-05-26'
summary: Notes on Chain of Thought
type: reading
---

## Why this paper?
This paper will serve as an introduction to reading papers. At first glance of the paper's title, I would like to learn more about what chain of thought is.

## Context
Ling et al. (2017) pioneered the idea of using natural language rationales to solve math word problems through a series
of intermediate steps (chain of thought). Their work is a remarkable contrast to the literature using formal languages
to reason (Roy et al., 2015; Chiang and Chen, 2019; Amini et al., 2019; Chen et al., 2019). Cobbe
et al. (2021) extend Ling et al. (2017) by creating a larger dataset and using it to finetune a pretrained
language model rather than training a model from scratch. In the domain of program synthesis,
Nye et al. (2021) leverage language models to predict the final outputs of Python programs via
first line-to-line predicting the intermediate computational results, and show that their step-by-step
prediction method performs better than directly predicting the final outputs. These approaches improve or augment the input part of the prompt (e.g., instructions that are prepended to inputs); this paper essentially zooms in on the orthogonal direction of augmenting the outputs of language models with a chain of thought by providing step by step reasoning to obtain the final answer.

## Problem Statement
Large Language Models prior to this research did not achieve high performance on challenging tasks such as arithmetic, commonsense, and symbolic reasoning. The contribution of this paper is to explore how reasoning ability of large language models can be augmented by a simple method known as chain of thought prompting. 

## Notes
To set this up, they didn't train or touch the model at all but rather they provided the model with additional context via prompting as such: [Input Question A] -> [Chain of Thought A] -> [Output Answer A] and then they ask a new question with [Input Question B].

## Questions
Initially, I did not understand what they meant by prepending the inputs with a chain of thought. After reading through the introduction I finally understand what they meant. They didn't have to train their models at all, just changing the way the prompt was written had a large effect on how the model can obtain logical reasoning. 

## Looking Forward
In this paper, chain of thought prompting was used for solving a complicated reasoning task such as a multi-step math word problem. I wonder if chain of thought prompting has been used for generating images via image diffusion or potentially even generating videos. I would imagine there is research done on this already so, this would be something worth reading more about.
