// should consider when it comes to the language of english
// should also consider the i18n

const FEATURE_LIST = {
  options: [
    {
      value: 1,
      label: 'general',
      children: [
        {
          value: 2,
          label: 'Token-count',
        },
        {
          value: 3,
          label: 'Type-count',
        },
        {
          value: 4,
          label: 'Spelling errors',
        },
        {
          value: 5,
          label: 'Compound errors',
        },
        {
          value: 6,
          label: 'Sentences',
        },
        {
          value: 7,
          label: 'Paragraphs',
        },
        {
          value: 8,
          label: 'Word length',
        },
        {
          value: 9,
          label: 'Sentence length (n words)',
        },
        {
          value: 10,
          label: 'Paragraph length (n words)',
        },
        {
          value: 11,
          label: 'Paragraph length (n sentences)',
        },
      ],
    },
    {
      value: 12,
      label: 'lexical',
      children: [
        {
          value: 13,
          label: 'A1 lemma INCSC',
        },
        {
          value: 14,
          label: 'A2 lemma INCSC',
        },
        {
          value: 15,
          label: 'B1 lemma INCSC',
        },
        {
          value: 16,
          label: 'B2 lemma INCSC',
        },
        {
          value: 17,
          label: 'C1 lemma INCSC',
        },
        {
          value: 18,
          label: 'C2 lemma INCSC',
        },
        {
          value: 19,
          label: 'Difficult Word INCSC',
        },
        {
          value: 20,
          label: 'Difficult Noun or Verb INCSC',
        },
        {
          value: 21,
          label: 'Out of Kelly-list INCSC',
        },
      ],
    },
    {
      value: 22,
      label: 'morph',
      children: [
        {
          value: 23,
          label: 'VERBFORM',
          children: [
            {
              value: 24,
              label: 'Modal VERB to VERB',
            },
            {
              value: 25,
              label: 'Present Participle to VERB',
            },
            {
              value: 26,
              label: 'Past Participle to VERB',
            },
            {
              value: 27,
              label: 'Present VERB to VERB',
            },
            {
              value: 28,
              label: 'Past VERB to VERB',
            },
            {
              value: 29,
              label: 'Supine VERB to VERB',
            },
          ],
        },
        {
          value: 30,
          label: 'PoS-PoS',
          children: [
            {
              value: 31,
              label: 'NOUN to VERB',
            },
            {
              value: 32,
              label: 'PRON to NOUN',
            },
            {
              value: 33,
              label: 'PRON to PREP',
            },
          ],
        },
        {
          value: 34,
          label: 'SubPoS-ALL',
          children: [
            {
              value: 35,
              label: 'S-VERB INCSC',
            },
          ],
        },
        {
          value: 36,
          label: 'PoS-ALL',
          children: [
            {
              value: 37,
              label: 'ADJ INCSC',
            },
            {
              value: 38,
              label: 'ADV INCSC',
            },
            {
              value: 39,
              label: 'NOUN INCSC',
            },
            {
              value: 40,
              label: 'PART INCSC',
            },
            {
              value: 41,
              label: 'PUNCT INCSC',
            },
            {
              value: 42,
              label: 'SCONJ INCSC',
            },
            {
              value: 43,
              label: 'VERB INCSC',
            },
          ],
        },
        {
          value: 44,
          label: 'PoS-MultiPoS',
          children: [
            {
              value: 45,
              label: 'ADJ Variation',
            },
            {
              value: 46,
              label: 'ADV Variation',
            },
            {
              value: 47,
              label: 'NOUN Variation',
            },
            {
              value: 48,
              label: 'VERB Variation',
            },
          ],
        },
        {
          value: 49,
          label: 'MultiPoS-MultiPoS',
          children: [
            {
              value: 50,
              label: 'CCONJ & SCONJ INCSC',
            },
            {
              value: 51,
              label: 'Functional Token INCSC',
            },
            {
              value: 52,
              label: 'Lex to Non-Lex',
            },
            {
              value: 53,
              label: 'Lex to Token',
            },
            {
              value: 54,
              label: 'Nominal Ratio',
            },
            {
              value: 55,
              label: 'Rel INCSC',
            },
          ],
        },
      ],
    },
    {
      value: 56,
      label: 'syntactic',
      children: [
        {
          value: 57,
          label: 'Dependency length', //
        },
        {
          value: 58,
          label: 'Dependency arcs longer than 5',
        },
        {
          value: 59,
          label: 'Longest dependency length',
        },
        {
          value: 60,
          label: 'Ratio of right dependency arcs',
        },
        {
          value: 61,
          label: 'Ratio of left dependency arcs',
        },
        {
          value: 62,
          label: 'Modifier variation',
        },
        {
          value: 63,
          label: 'Pre-modifier INCSC',
        },
        {
          value: 64,
          label: 'Post-modifier INCSC',
        },
        {
          value: 65,
          label: 'Subordinate INCSC',
        },
        {
          value: 66,
          label: 'Relative clause INCSC',
        },
        {
          value: 67,
          label: 'Prepositional complement INCSC',
        },
      ],
    },
  ],
};

const SWEDISH_ONLY_FEATURES = {
  options: [
    {
      value: 12,
      label: 'lexical',
      children: [
        {
          value: 68,
          label: 'Kelly log-frequency', // swedish only
        },
      ],
    },
    {
      value: 22,
      label: 'morph',
      children: [
        {
          value: 23,
          label: 'VERBFORM',
          children: [
            {
              value: 69,
              label: 'S-VERB to VERB', // swedish only
            },
          ],
        },
        {
          value: 34,
          label: 'SubPoS-ALL',
          children: [
            {
              value: 70,
              label: 'Neuter Gender NOUN INCSC', // Swedish only
            },
          ],
        },
      ],
    },
    {
      value: 71,
      label: 'readability',
      children: [
        {
          value: 72,
          label: 'LIX',
        },
        {
          value: 73,
          label: 'OVIX',
        },
        {
          value: 74,
          label: 'Typ-token ratio(rotbaserad)',
        },
        {
          value: 75,
          label: 'Enkel nominalkvot',
        },
        {
          value: 76,
          label: 'Full nominalkvot',
        },
      ],
    },
  ],
};

const ENGLISH_ONLY_FEATURES = {
  options: [
    {
      value: 68,
      label: 'readability',
      children: [
        {
          value: 69,
          label: 'Bilogarithm TTR',
        },
        {
          value: 70,
          label: 'Root TTR',
        },
        {
          value: 71,
          label: 'Coleman Liau Index',
        },
        {
          value: 72,
          label: 'Flesch Reading Ease',
        },
        {
          value: 73,
          label: 'Flesch Kincaid Grade level',
        },
        {
          value: 74,
          label: 'Automated Readability Index',
        },
        {
          value: 75,
          label: 'SMOG',
        },
      ],
    },
  ],
};

export const ENGLISH_FEATURES = {
  options: [
    ...FEATURE_LIST.options,
    ...ENGLISH_ONLY_FEATURES.options,
  ],
};

export const SWEDISH_FEATURES = {
  options: [
    ...FEATURE_LIST.options.map((option) => {
      if (option.label === 'lexical') {
        return {
          ...option,
          children: [
            ...option.children,
            ...SWEDISH_ONLY_FEATURES.options[0].children,
          ],
        };
      } if (option.label === 'morph') {
        return {
          ...option,
          children: option.children.map((child) => {
            if (child.label === 'VERBFORM') {
              return {
                ...child,
                children: [
                  ...child.children,
                  ...SWEDISH_ONLY_FEATURES.options[1].children[0].children,
                ],
              };
            } if (child.label === 'SubPoS-ALL') {
              return {
                ...child,
                children: [
                  ...child.children,
                  ...SWEDISH_ONLY_FEATURES.options[1].children[1].children,
                ],
              };
            }
            return child;
          }),
        };
      }
      return option;
    }),
    SWEDISH_ONLY_FEATURES.options[2],
  ],
};
