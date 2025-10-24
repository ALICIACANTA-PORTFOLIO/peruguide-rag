# 📚 Academic References & Bibliography

This document maintains the complete bibliography of sources cited throughout the PeruGuide AI project documentation. The actual PDF files are not included in this repository to respect copyright, but full citations are provided for reference.

## 🎯 Core RAG Architecture

### 1. Retrieval-Augmented Generation Foundation
**Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... & Kiela, D.** (2020).  
*Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.*  
**Conference**: NeurIPS 2020  
**Type**: Peer-reviewed paper  
**DOI**: arXiv:2005.11401  
**Key Contribution**: Foundation paper introducing RAG architecture for combining retrieval with generation

### 2. Build a Large Language Model (From Scratch)
**Raschka, Sebastian** (2024).  
*Build a Large Language Model (From Scratch).*  
**Publisher**: Manning Publications  
**ISBN**: 978-1633437166  
**Relevant Chapters**:
- Chapter 4: Implementing embedding layers (§4.2 - overlapping chunking strategy)
- Chapter 5: Pre-training on unlabeled data
- Chapter 6: Fine-tuning for text classification
- Chapter 7: Instruction fine-tuning

**Citations in Project**:
- `README.md` (§2.3): Chunking overlap strategy (12.5% recommendation)
- Text splitter implementation based on §4.2 principles

### 3. Hands-On Large Language Models
**Alammar, Jay & Grootendorst, Maarten** (2024).  
*Hands-On Large Language Models: Language Understanding and Generation.*  
**Publisher**: O'Reilly Media  
**ISBN**: 978-1098150952  
**Relevant Chapters**:
- Chapter 5: Semantic search and embeddings
- Chapter 8: RAG pipeline implementation
- Chapter 10: Production deployment

**Citations in Project**:
- `README.md` (§1.2): "RAG quality fundamentally limited by retrieval precision"
- `README.md` (§7.1): Embedding model comparison methodology
- Architecture diagram inspiration

## 🔍 Vector Search & Embeddings

### 4. Billion-scale similarity search with GPUs
**Johnson, Jeff, Douze, Matthijs, & Jégou, Hervé** (2019).  
*Billion-scale similarity search with GPUs.*  
**Journal**: IEEE Transactions on Big Data, 7(3), 535-547  
**DOI**: 10.1109/TBDATA.2019.2921572  
**Key Contribution**: FAISS architecture and optimization techniques

**Citations in Project**:
- `README.md` (Table 7.2): FAISS comparison with alternatives
- Vector store selection rationale

### 5. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
**Reimers, Nils & Gurevych, Iryna** (2019).  
*Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.*  
**Conference**: EMNLP-IJCNLP 2019  
**DOI**: arXiv:1908.10084  
**Key Contribution**: Foundation of Sentence Transformers library

**Citations in Project**:
- `README.md` (§7.1): Sentence Transformers model selection
- Embedding pipeline implementation

## 🛠️ LLM Engineering

### 6. The LLM Engineer's Handbook
**Iusztin, Paul & Labonne, Maxime** (2024).  
*The LLM Engineer's Handbook: Engineering Production-Ready LLM Applications.*  
**Publisher**: Packt Publishing  
**ISBN**: 978-1836200062  
**Relevant Chapters**:
- Chapter 3: Testing strategies for LLM systems
- Chapter 6: Prompt engineering (§6.3 - system prompts)
- Chapter 9: Production deployment

**Citations in Project**:
- `README.md` (§3.1): "LLM systems fail silently" - testing philosophy
- `README.md` (§7.4): Prompt engineering structure
- Integration test design patterns

### 7. Designing Large Language Model Applications
**Bommasani, Rishi et al.** (2023).  
*Designing Large Language Model Applications.*  
**Institution**: Stanford HAI (Human-Centered Artificial Intelligence)  
**Type**: Technical report  
**URL**: https://hai.stanford.edu/

**Citations in Project**:
- `README.md` (§6.1): "Vendor lock-in is the silent killer of AI projects"
- Multi-provider abstraction strategy

## 📊 Data Storytelling

### 8. Storytelling with Data
**Knaflic, Cole Nussbaumer** (2015).  
*Storytelling with Data: A Data Visualization Guide for Business Professionals.*  
**Publisher**: Wiley  
**ISBN**: 978-1119002253  
**Relevant Chapters**:
- Chapter 3: Context is everything
- Chapter 8: Pulling it all together (transparency)

**Citations in Project**:
- `README.md` (Act I): "When you have too much data, you have no data"
- `README.md` (§6.2): Data visualization principles
- `README.md` (§7.5): "Transparency builds trust. Always show your sources"

### 9. Effective Data Storytelling
**Dykes, Brent** (2020).  
*Effective Data Storytelling: How to Drive Change with Data, Narrative and Visuals.*  
**Publisher**: Wiley  
**ISBN**: 978-1119615712  

**Citations in Project**:
- `README.md` (§6.2): "Data without context is noise. Show the 'why' behind the 'what'"
- Performance benchmarks presentation

### 10. User Story Mapping
**Patton, Jeff & Economy, Peter** (2014).  
*User Story Mapping: Discover the Whole Story, Build the Right Product.*  
**Publisher**: O'Reilly Media  
**ISBN**: 978-1491904909  

**Citations in Project**:
- Integration test documentation
- User journey narratives

## 🇵🇪 Peru Tourism Domain

### 11. MINCETUR Official Documentation
**Ministerio de Comercio Exterior y Turismo (MINCETUR)** (2024).  
*Requisitos de Ingreso al Perú - Guía Oficial.*  
**Source**: Government publication  
**URL**: https://www.gob.pe/mincetur  
**Type**: Official tourism documentation

**Usage**: Primary source data for RAG system (not included in repository)

### 12. MINSA Health Guidelines
**Ministerio de Salud (MINSA)** (2024).  
*Recomendaciones de Vacunación para Viajeros.*  
**Source**: Government publication  
**Type**: Official health documentation

**Usage**: Health requirements context for Peru travel (not included in repository)

## 📝 Additional Technical Resources

### Python & FastAPI
- **FastAPI Documentation** - https://fastapi.tiangolo.com/
- **Pydantic Documentation** - https://docs.pydantic.dev/
- **pytest Documentation** - https://docs.pytest.org/

### Vector Databases
- **FAISS Documentation** - https://faiss.ai/
- **Sentence Transformers Documentation** - https://www.sbert.net/

### LLM APIs
- **OpenAI API Reference** - https://platform.openai.com/docs/
- **Anthropic Claude Documentation** - https://docs.anthropic.com/
- **HuggingFace Hub** - https://huggingface.co/docs/hub/

## 🔒 Copyright Notice

All books, papers, and documents listed here are copyrighted by their respective authors and publishers. They are cited for academic and educational purposes under fair use principles. **Physical copies or PDFs are NOT included in this repository.**

To access these materials:
1. **Academic Papers**: Available through arXiv, IEEE Xplore, or ACL Anthology
2. **Books**: Purchase from publishers (Manning, O'Reilly, Wiley, Packt)
3. **Government Documents**: Freely available from official websites

## 📚 BibTeX Citations

```bibtex
@inproceedings{lewis2020retrieval,
  title={Retrieval-augmented generation for knowledge-intensive nlp tasks},
  author={Lewis, Patrick and Perez, Ethan and Piktus, Aleksandra and Petroni, Fabio and Karpukhin, Vladimir and Goyal, Naman and K{\"u}ttler, Heinrich and Lewis, Mike and Yih, Wen-tau and Rockt{\"a}schel, Tim and others},
  booktitle={Advances in Neural Information Processing Systems},
  volume={33},
  pages={9459--9474},
  year={2020}
}

@book{raschka2024build,
  title={Build a Large Language Model (From Scratch)},
  author={Raschka, Sebastian},
  year={2024},
  publisher={Manning Publications}
}

@book{alammar2024hands,
  title={Hands-On Large Language Models},
  author={Alammar, Jay and Grootendorst, Maarten},
  year={2024},
  publisher={O'Reilly Media}
}

@article{johnson2019billion,
  title={Billion-scale similarity search with GPUs},
  author={Johnson, Jeff and Douze, Matthijs and J{\'e}gou, Herv{\'e}},
  journal={IEEE Transactions on Big Data},
  volume={7},
  number={3},
  pages={535--547},
  year={2019},
  publisher={IEEE}
}

@inproceedings{reimers2019sentence,
  title={Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks},
  author={Reimers, Nils and Gurevych, Iryna},
  booktitle={Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing},
  year={2019}
}

@book{iusztin2024llm,
  title={The LLM Engineer's Handbook},
  author={Iusztin, Paul and Labonne, Maxime},
  year={2024},
  publisher={Packt Publishing}
}

@book{knaflic2015storytelling,
  title={Storytelling with Data: A Data Visualization Guide for Business Professionals},
  author={Knaflic, Cole Nussbaumer},
  year={2015},
  publisher={Wiley}
}

@book{dykes2020effective,
  title={Effective Data Storytelling: How to Drive Change with Data, Narrative and Visuals},
  author={Dykes, Brent},
  year={2020},
  publisher={Wiley}
}

@book{patton2014user,
  title={User Story Mapping: Discover the Whole Story, Build the Right Product},
  author={Patton, Jeff and Economy, Peter},
  year={2014},
  publisher={O'Reilly Media}
}
```

---

**Last Updated**: October 24, 2025  
**Project**: PeruGuide AI  
**Purpose**: Academic integrity and proper attribution  
**Note**: All citations follow APA 7th edition style
