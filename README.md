<div align="center">

# 🎓 Accreditation Copilot

### Hybrid RAG System for NAAC & NBA Accreditation Compliance

🚀 Intelligent document retrieval system combining FAISS (dense) + BM25 (sparse) with neural reranking for high-precision results.

<br>

🌐 **Live Demo:** http://13.232.129.54:3000
🎬 **Video Demo:** https://www.youtube.com/watch?v=B8WUaarxMPM
💻 **Repository:** https://github.com/Effec77/Omni-Accreditation-Assistant

</div>

---

## 🌟 Overview

**Accreditation Copilot** is a high-performance Retrieval-Augmented Generation (RAG) system designed to assist educational institutions in navigating complex accreditation frameworks such as **NAAC** and **NBA**.

The system leverages hybrid retrieval techniques and optimized data pipelines to deliver **accurate, context-rich responses in ~900ms**, enabling efficient document understanding and compliance analysis.

---

## ⚡ Key Highlights

* 🔍 **Hybrid Retrieval:** FAISS (dense) + BM25 (sparse) with Reciprocal Rank Fusion
* 🧠 **Context Optimization:** Parent-child chunk expansion (2.8× enrichment)
* ⚡ **Performance:** ~900ms query latency
* 🎯 **Accuracy:** Precision@1 = 80%, Precision@5 = 100%
* 🧩 **Reranking:** Cross-encoder based relevance scoring

---

## 🏗️ System Architecture

* Query Expansion → Hybrid Retrieval → Fusion → Reranking → Context Expansion → Final Results
* Designed for **scalable, performance-efficient AI systems**

---

## 📊 Performance Metrics

| Metric            | Value  |
| ----------------- | ------ |
| Query Latency     | ~900ms |
| Precision@1       | 80%    |
| Precision@5       | 100%   |
| Context Expansion | 2.8×   |
| GPU Usage         | ~15%   |

---

## 🛠️ Tech Stack

* **Language:** Python
* **ML/DL:** PyTorch, Transformers
* **Retrieval:** FAISS, BM25
* **Database:** SQLite
* **LLM API:** Groq
* **Processing:** PyMuPDF

---

## 🚀 Quick Start

```bash
git clone <repository-url>
cd accreditation_copilot

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

---

## ⚠️ Note on Demo

> The live demo may occasionally be unavailable due to server limitations. Please refer to the video demo for full functionality.

---

## 🤝 Contribution

This project was developed collaboratively, with contributions in **system design, retrieval optimization, and evaluation pipelines**.

---

## 📌 Status

✅ Phase 2 Complete (Hybrid Retrieval + Optimization)
🔄 Phase 3 (Answer Generation) in progress

---

⭐ *If you find this useful, consider starring the repository!*
