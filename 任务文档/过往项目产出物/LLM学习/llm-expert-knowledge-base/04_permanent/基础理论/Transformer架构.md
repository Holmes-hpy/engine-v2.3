# Transformer架构

## 概述

Transformer是现代大语言模型（LLM）的核心架构，于2017年在论文《Attention Is All You Need》中提出。它完全基于注意力机制，摒弃了传统的循环神经网络（RNN）结构。

## 架构组成

### 编码器-解码器结构
原始的Transformer采用编码器-解码器结构：
- **编码器**：处理输入序列，将其转换为语义表示
- **解码器**：根据编码器输出和之前生成的内容生成输出序列

### 现代演变
现代的大语言模型主要采用**仅解码器（decoder-only）**架构：
- GPT系列：OpenAI的GPT-1、GPT-2、GPT-3、GPT-4
- Llama系列：Meta的Llama、Llama 2、Llama 3
- Mistral系列：Mistral-7B等

## 核心组件

### 1. 词嵌入层
将文本tokens转换为向量表示，每个token对应一个高维向量。

### 2. 位置编码
为每个位置添加位置信息，使模型能够理解词语的顺序。

### 3. 自注意力机制
- **查询（Query）**、**键（Key）**、**值（Value）**
- 多头注意力：并行使用多个注意力头
- 因果注意力：在生成时仅关注之前的tokens

### 4. 前馈神经网络
每个注意力层后都有一个全连接的前馈网络。

### 5. 层归一化和残差连接
- 层归一化：保持训练稳定性
- 残差连接：避免梯度消失

## 生成过程

### Tokenization
将输入文本转换为token序列。

### 自回归生成
一次生成一个token：
1. 预测下一个token的概率分布
2. 采样或选择token
3. 将新token加入输入序列
4. 重复直到完成

### 采样策略
- 贪婪搜索：选择概率最高的token
- 束搜索：维护多个候选序列
- 温度采样：调整概率分布的锐度
- 核采样（top-p）：累积概率到p后截断

## 重要论文

- 《Attention Is All You Need》 - Vaswani et al. (2017)
- 《Improving Language Understanding by Generative Pre-Training》 - OpenAI (2018)

## 相关概念

- [注意力机制](./attention机制.md)
- [大模型训练](./大模型预训练.md)
- [推理优化](./推理优化技术.md)


---

审计信息：
- 审计时间：2026-06-06 16:50:12
- 综合得分：82.8
- 优化建议：建议进一步补充技术细节和示例代码
