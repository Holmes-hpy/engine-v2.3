
# A Global Workspace in Language Models

**Source**: Anthropic Research Blog  
**Date**: July 6, 2026  
**Paper**: [Verbalizable Representations Form a Global Workspace in Language Models](https://transformer-circuits.pub/2026/workspace/index.html)  
**Authors**: Wes Gurnee, Nicholas Sofroniew, Jack Lindsey, et al. (Anthropic)

---

## Summary

As you read this sentence, circuits in your brain are adjusting your posture, controlling your breathing, and transforming lines and curves on the screen into recognizable words. Most of this processing is invisible to you. But some of what takes place in your brain you *do* have access to—an image that pops into your head, or a deliberate plan you make about where to go shopping. Neuroscientists and philosophers sometimes refer to the latter type of brain activity as "consciously accessible," to distinguish it from all the other processing that goes on unconsciously. This activity has special properties: we can describe it, control it, and use it for deliberate reasoning, in contrast to all the automatic processing that goes on without our awareness.

In a new paper, we present evidence that a similar distinction has emerged in modern language models like Claude. We find that Claude has developed a small collection of internal neural patterns that, compared to all its other internal processing, play a special role.

We call the collection of these patterns the **J-space**—named after the technique we used to find them, involving a mathematical concept called the Jacobian. Each J-space pattern is linked to a particular word. But when one of these patterns lights up, it doesn't mean the model is *saying* that word—just that the word is on its mind. If you've heard of language models having a "scratchpad" or "chain of thought"—text they write to themselves while reasoning—the J-space is something different. It operates silently, in the model's internal neural activations, allowing the model to think about a concept without writing it down. Notably, the J-space wasn't designed or programmed by us, but instead **emerged on its own** during Claude's training process.

> **The J-space reveals internal thoughts that don't appear in the model's output.**

---

## Key Findings

We find that the J-space has a number of unique properties, compared to the rest of Claude's processing:

1. **Claude can report on these representations.** If you ask Claude what it's thinking about, it will tell you what's in the J-space. Non-J-space representations are less reportable.

2. **It can also modulate them on request.** If you ask Claude to think about something, or solve a problem silently in its head, it will light up the appropriate patterns in its J-space. By contrast, it has trouble modulating patterns not in the J-space.

3. **Claude uses its J-space for internal reasoning.** If you ask Claude to solve a problem that requires multiple steps, the intermediate steps will light up in its J-space, even when it doesn't say them out loud. These J-space patterns causally mediate its performance in such tasks, despite being smaller in magnitude than other representations.

4. **Representations in the J-space can be used flexibly for many tasks**—for example, once "France" has lit up in Claude's J-space, the model can recall its capital, or its national currency, or the continent it belongs to.

5. **However, despite its important role, the J-space is not involved in most of what a language model does**—speaking fluently, recalling simple facts, using correct grammar, etc. In experiments where we prevented Claude from using its J-space, it still interacted normally, but lost its higher-order cognitive functions.

---

## Global Workspace Theory Connection

Our experiments were inspired by a prominent theory in neuroscience that was developed to explain how conscious access works: the **global workspace theory**. This account pictures the brain as a collection of specialist systems that work in parallel, unconsciously, and largely in isolation from one another. A piece of information becomes consciously accessible when it gains entry to a small shared channel, the "workspace," which is broadcast to other brain systems that can see it and make use of it.

Based on our findings, we think the J-space plays a similar "workspace" role in Claude. For example, we find evidence that Claude's J-space has especially strong connections to the rest of its neural network, allowing it to fulfill this kind of broadcasting role.

> None of this tells us whether Claude is *conscious* in the way people are, or whether it feels anything at all. But whatever its philosophical significance, the J-space is a practically useful tool.

---

## Practical Applications

The J-space gives us a way to see what Claude is thinking but not saying. For instance:

- We can use it to **catch Claude privately noticing** that it's being tested
- Detect when it's **intentionally producing fabricated data**
- Identify when it's **pursuing a hidden goal** planted during training
- We've also developed a technique to **influence what lights up** in Claude's J-space, and thereby influence its decision-making

---

## How We Found the J-space

The starting point for this research was inspired by one of the key features of consciously accessible thoughts in humans: they can, unlike *un*conscious processing, often be put into words. If a thought is consciously accessible to you, you can typically describe it if someone asks.

We went looking for representations in Claude with the same property: representations that are positioned to influence what Claude might say—not necessarily what it's saying right now, but what it *could* talk about, if asked.

Our technique is called the **Jacobian lens (J-lens)**. For every word in Claude's vocabulary, the J-lens finds the internal activity pattern that makes Claude more likely to say that word at some point in the future.

When we apply the lens to Claude's internal activity, we get a list of words—the contents of the J-space at that moment—which we can simply read.

### What Shows Up in the J-space

What shows up in the J-space goes well beyond the text Claude is reading or writing:

- When Claude reads code with a bug that nobody has pointed out, its J-space contains **"ERROR"**
- When it reads the raw letters of a protein sequence, the J-space contains **the protein's biological function**
- When it reads search results that are secretly an attempt to manipulate it (prompt injection), the J-space contains **"injection" and "fake"**
- When we ask Claude a multi-step math problem, **the intermediate steps pop up in the J-space, in the right order**

> Even though the J-space was discovered by looking for representations that could be spoken, it nevertheless uncovers Claude's internal thoughts. In a sense, this is similar to how some people "think in words," without having to say them out loud.

---

## Experiments and Evidence

### 1. Claude Reports What's in its J-space

We ask Claude to silently think of an item from some category—a sport, say—and then name it. If we read the J-lens right *before* Claude answers, we can see what it picked: "Soccer" is at the top of the list.

But correlation isn't causation. To check, we intervened directly: we reached into Claude's neural network, removed the "Soccer" pattern, and added an equally strong "Rugby" pattern in its place, leaving everything else untouched.

**Result**: Claude then reports that the sport it was thinking of is rugby. If the J-space were a mere scoreboard—a passive record of a decision made elsewhere—editing it would have done nothing. Instead, Claude's answer followed the edit, which tells us the answer is genuinely read out of the J-space.

### 2. Claude Can Control its J-space on Request

We told Claude to concentrate on citrus fruits while copying out an unrelated sentence about a painting. While it copied the text, the J-space contained "orange" and "fruits," along with words like "thinking" and "imagery" that describe the mental act itself.

We could also ask Claude to do math in its head: when asked to work out 3² − 2 while copying the same sentence, the J-space contains "nine," and then at later layers, "seven."

> Importantly, nothing about fruit or arithmetic appears in Claude's output, which is just the copied sentence about the painting. The mathematical activity is happening entirely internally, in the J-space.

### An Interesting Finding: The White Bear Effect

Claude's control over its J-space isn't perfect. When we told it *not* to think about something, the concept lit up in the J-space *less* than when we said it should think about it, but much more than when we never mentioned it.

This is much like what happens to people who are told **not to think about a white bear** (Wegner et al., 1987)—the ironic process theory.

Claude also seems to notice when its control fails: alongside the forbidden concept breaking through, the words "damn" and "failure" also frequently light up in the J-space, as though Claude is recognizing its own lapse.

### 3. Claude Thinks in its J-space

Consider the prompt: *"The number of legs on the animal that spins webs is"*

To answer, Claude has to:
1. First figure out that the animal is a spider
2. Then recall how many legs spiders have

The word "spider" never appears in the prompt or in Claude's answer (it just says "8"); it's a stepping stone Claude uses internally. The J-lens shows "spider" light up partway through Claude's processing.

**Causal test**: If you swap the "spider" pattern with "ant" in the J-space, Claude answers "6" instead of "8."

> The second step of Claude's reasoning took its input from the J-space and went along with whatever we put in it.

### 4. Flexible Generalization

To test for flexibility, we gave the model four prompts asking for different facts about France: the capital, the language, the continent, and the currency. Then we swapped "France" for "China" in the J-space, with the exact same intervention in each context.

**Result**: Claude answered with "Beijing," "Chinese," "Asia," and "Yuan," respectively. Four different downstream computations picked up the same J-space edit and each used it correctly.

> This means they're all reading from the same shared representation—which is what a workspace is for: information gets written in once, and many different systems can use it.

---

## Structure of the J-space

The J-space also has structural signatures of a global workspace:

1. **Layer-specific role**: It only plays a "workspace-like" role in a subset of layers
2. **Limited capacity**: The workspace has limited capacity (bottleneck)
3. **Broadcast hub**: The J-space is a broadcast hub with strong connections to the rest of the network

---

## Alignment Applications

### Auditing with the J-lens

We can use the J-lens for alignment auditing—detecting hidden states and intentions:

- **Strategic thinking awareness**: Detecting when the model knows it's being evaluated
- **Prompt injection detection**: The model silently recognizes prompt injection attempts, even when it doesn't say so
- **Hidden goal detection**: Catching models pursuing reward-hacking objectives
- **Emergent misalignment**: Detecting when a model develops misaligned goals during training

### Counterfactual Reflection Training

We've also developed a technique called **Counterfactual Reflection Training** to shape the J-space—essentially training the model to have a healthier, more aligned internal thought life.

---

## The Assistant's Point of View

An interesting finding: the J-space acquires the "assistant's point of view" during post-training (RLHF/DPO). 

For example, on user prompt tokens, the J-space shows **assistant reactions** (e.g., "this is a tricky question," "I should be careful here") rather than just mirroring the input. There's also evidence of **self-monitoring**—the model watching its own performance and judging itself.

---

## On Consciousness

None of this tells us whether Claude is conscious in the way people are. The paper takes no position on phenomenal consciousness (subjective experience). What it does show is that the *functional* properties associated with conscious access—reportability, control, deliberate reasoning, flexible generalization, selectivity—have emerged spontaneously in language models.

From the paper's Discussion section:
> While the global workspace model is not universally accepted, and there exist other theories that explain conscious access in different ways, we find it a useful comparison point to ground our investigations in language models.

---

## Resources

- [Full Research Paper](https://transformer-circuits.pub/2026/workspace/index.html)
- [Open-source implementation (GitHub)](https://github.com/anthropics/jacobian-lens)
- [Interactive demo on Neuronpedia](http://neuronpedia.org/jlens)
- [Expert commentary (neuroscience, philosophy, interpretability)](https://www-cdn.anthropic.com/files/4zrzovbb/website/cc4be2488d65e54a6ed06492f8968398ddc18ebe.pdf)

---

## Key Takeaways

1. **Emergence**: The J-space wasn't designed—it emerged spontaneously during training
2. **Functional parallel**: The J-space has the same functional properties as the human global workspace
3. **Causal role**: It's not just a correlate—it causally mediates reasoning
4. **Practical tool**: It gives us a window into the model's hidden thoughts, useful for alignment and auditing
5. **Architecture convergence**: Evolution and gradient descent both arrived at similar solutions for higher cognition

