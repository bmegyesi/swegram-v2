<h1>Pipeline Workflow on the basis of parameter setting</h1>

<p>Pipeline for the language of English works similarly with Swedish. This description focuses on how to integrate different parameter setting with file checkers.</p>

```
pipeline
  - upload file
    - check if there is metadata
      - Yes, convert file into texts
      - No
    - Reading setting
      - tokenization (this includes sentence segmentation, this parameter is always on.)
      - normalization (if the text goes through spelling checker)
      - Lemmartization, PoS tagging and parsing
      - annotation (if the texts in the file are annotated)
        - if text is annotated
            - if normalization and parsing are on
              go to checker (normalization=true, parsing=true)
            - elif normalization is on
              go to checker (normalization=true, parsing=false)
            - elif parsing is on
              go to checker (normalization=true, parsing=false)
            - else
              go to checker (normalizatio=true, parsing=false)
        - else
            generate options given the setting of normalization and parsing.
```