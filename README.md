# Lyricutils

A modern, extensible Python library to **download, create, and align lyrics** with precision and control.

---
## Key features

* **Multi-Backend Support**: Seamlessly switch between mutliple backend providers for forced-alignment.
* **Lyric Alignment**: Tools to sync text to audio timestamps.
* **Modern Python**: Built for Python 3.11+ using type hints and async-first principles.
* **Extensible Architecture**: Easily plug in your own custom lyric providers.

## Caching
```mermaid
flowchart TD
    A[Input: Messy File] --> B{Check file_map}
    B -- Found --> C[Get ISRC]
    B -- Not Found --> D[Resolver]
    D --> E[Save to tracks & file_map]
    E --> C
    C --> F{Check lyrics}
    F -- Not Found --> G[Provider]
    G --> H[Save to lyrics]
    H --> I[Ready for Aligner]
    F -- Found --> I
    I --> J{Check task_hash}
    J -- Found --> K[Return Cached JSON]
    J -- Not Found --> L[Run AI Aligner]
    L --> M[Save to alignments]
    M --> K
```
