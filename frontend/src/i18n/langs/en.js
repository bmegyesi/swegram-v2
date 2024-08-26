import elementEN from 'element-ui/lib/locale/lang/en';

const en = {
  features: {
    general: 'General features', // block name
    lexical: 'Lexical features', // block name
    morph: 'Morphological features', // block name
    syntactic: 'Syntactic features', // block name
    readability: 'Readability features', // block name

    tokenCount: 'Tokens',
    typeCount: 'Types',
    spellingErrors: 'Spelling errors',
    compoundErrors: 'Compound errors',
    sentences: 'Sentences',
    paragraphs: 'Paragraphs',
    wordLength: 'Word length',
    sentenceLengthNWords: 'Sentence length (n words)',
    paragraphLengthNWords: 'Paragraph length (n words)',
    paragraphLengthNSentences: 'Paragraph length (n sentences)',

    lix: 'LIX',
    ovix: 'OVIX',
    typTokenRatiorotbaserad: 'Type-token ratio',
    enkelNominalkvot: 'Simple nominal ratio',
    fullNominalkvot: 'Full nominal ratio',

    bilogarithmTtr: 'Bilogarithm TTR',
    rootTtr: 'Root TTR',
    colemanLiauIndex: 'Coleman Liau Index',
    fleschReadingEase: 'Flesch Reading Ease',
    fleschKincaidGradeLevel: 'Flesch Kincaid Grade level',
    automatedReadabilityIndex: 'Automated Readability Index',
    smog: 'SMOG',

    a1LemmaIncsc: 'A1 Lemma',
    a2LemmaIncsc: 'A2 Lemma',
    b1LemmaIncsc: 'B1 Lemma',
    b2LemmaIncsc: 'B2 Lemma',
    c1LemmaIncsc: 'C1 Lemma',
    c2LemmaIncsc: 'C2 Lemma',
    difficultWordIncsc: 'Difficult Word',
    difficultNounOrVerbIncsc: 'Difficult Noun or Verb',
    outOfKellyListIncsc: 'Out of Kelly list',
    kellyLogFrequency: 'Kelly log frequency',

    verbform: 'VERBFORM',
    posPos: 'PoS-PoS',
    subposAll: 'SUBPoS-ALL',
    posAll: 'PoS-ALL',
    posMultipos: 'PoS-MultiPoS',
    multiposMultipos: 'MultiPoS-MultiPoS',

    posAll_adjIncsc: 'PoS-ALL ADJ INCSC',
    posAll_advIncsc: 'PoS-ALL ADV INCSC',
    posAll_nounIncsc: 'PoS-ALL NOUN INCSC',
    posAll_partIncsc: 'PoS-ALL PART INCSC',
    posAll_punctIncsc: 'PoS-ALL PUNCT INCSC',
    posAll_sconjIncsc: 'PoS-ALL SCONJ INCSC',
    posAll_verbIncsc: 'PoS-ALL VERB INCSC',

    posPos_nounToVerb: 'PoS-PoS NOUN to VERB',
    posPos_pronToNoun: 'PoS-PoS PRON to NOUN',
    posPos_pronToPrep: 'PoS-PoS PRON to PREP',

    'subposAll_s-verbIncsc': 'SUBPoS-ALL S-VERB INCSC',
    subposAll_neuterGenderNounIncsc: 'Neuter Gender NOUN INCSC',

    verbform_modalVerbToVerb: 'VERBFORM Modal VERB to VERB',
    verbform_presentParticipleToVerb: 'VERBFORM Present Participle to VERB',
    verbform_pastParticipleToVerb: 'VERBFORM Past Participle to VERB',
    verbform_presentVerbToVerb: 'VERBFORM Present VERB to VERB',
    verbform_pastVerbToVerb: 'VERBFORM Past VERB to VERB',
    verbform_supineVerbToVerb: 'VERBFORM Supine VERB to VERB',
    verbform_sVerbToVerb: 'VERBFORM S-VERB to VERB',

    posMultipos_adjVariation: 'PoS-MultiPoS ADJ Variation',
    posMultipos_advVariation: 'PoS-MultiPoS ADV Variation',
    posMultipos_nounVariation: 'PoS-MultiPoS NOUN Variation',
    posMultipos_verbVariation: 'PoS-MultiPoS VERB Variation',

    multiposMultipos_cconjSconjIncsc: 'MultiPoS-MultiPoS CCONJ & SCONJ INCSC',
    multiposMultipos_functionalTokenIncsc: 'MultiPoS-MultiPoS Functional Token INCSC',
    'multiposMultipos_lexToNon-lex': 'MultiPoS-MultiPoS Lex to Non-lex',
    multiposMultipos_lexToToken: 'MultiPoS-MultiPoS Lex to Token',
    multiposMultipos_nominalRatio: 'MultiPoS-MultiPoS Nominal Ratio',
    multiposMultipos_relIncsc: 'MultiPoS-MultiPoS Rel INCSC',

    modalVerbToVerb: 'Modal VERB to VERB',
    presentParticipleToVerb: 'Present Participle to VERB',
    pastParticipleToVerb: 'Past Participle to VERB',
    presentVerbToVerb: 'Present VERB to VERB',
    pastVerbToVerb: 'Past VERB to VERB',
    supineVerbToVerb: 'Supine VERB to VERB',
    sVerbToVerb: 'S-VERB to VERB',

    nounToVerb: 'NOUN to VERB',
    pronToNoun: 'PRON to NOUN',
    pronToPrep: 'PRON to PREP',

    sVerbIncsc: 'S-VERB INCSC',
    neuterGenderNounIncsc: 'Neuter Gender NOUN INCSC',

    adjIncsc: 'ADJ INCSC',
    advIncsc: 'ADV INCSC',
    nounIncsc: 'NOUN INCSC',
    partIncsc: 'PART INCSC',
    punctIncsc: 'PUNCT INCSC',
    sconjIncsc: 'SCONJ INCSC',
    verbIncsc: 'VERB INCSC',

    adjVariation: 'ADJ Variation',
    advVariation: 'ADV Variation',
    nounVariation: 'NOUN Variation',
    verbVariation: 'VERB Variation',

    cconjSconjIncsc: 'CCONJ & SCONJ INCSC',
    functionalTokenIncsc: 'Functional Token INCSC',
    lexToNonLex: 'Lex to Non-lex',
    lexToToken: 'Lex to Token',
    nominalRatio: 'Nominal Ratio',
    relIncsc: 'Rel INCSC',

    dependencyLength: 'Dependency length', // syntactic name
    dependencyArcsLongerThan5: 'Dependency arcs longer than 5', // syntactic features
    longestDependencyLength: 'Longest dependency length', // syntactic features
    ratioOfRightDependencyArcs: 'Ratio of right dependency arcs', // syntactic features
    ratioOfLeftDependencyArcs: 'Ratio of left dependency arcs', // syntactic features
    modifierVariation: 'Modifier variation', // syntactic features
    preModifierIncsc: 'Pre-modifier INCSC', // syntactic features
    postModifierIncsc: 'Post-modifier INCSC', // syntactic features
    subordinateIncsc: 'Subordinate INCSC', // syntactic features
    relativeClauseIncsc: 'Relative clause INCSC', // syntactic features
    prepositionalComplementIncsc: 'Prepositional complement INCSC', // syntactic features
  },
  featuresDef: {
    tokenCount: 'Counts of Tokens',
    typeCount: 'Counts of types',
    spellingErrors: 'Counts of Spelling errors',
    compoundErrors: 'Counts of Compound errors',
    sentences: 'Counts of Sentences',
    paragraphs: 'Counts of Paragraphs',
    wordLength: 'Counts of Characters per word',
    sentenceLengthNWords: 'Counts of words per sentence',
    paragraphLengthNWords: 'Counts of words per paragraph',
    paragraphLengthNSentences: 'Counts of sentences per paragraph',

    lix: 'f(LIX) = Counts(words)/Counts(sentences) + Counts(long words) * 100 / Counts(words)',
    ovix: 'f(OVIX) = In(tokens) / ( In( 2 - In(types)/In(tokens) ) )',
    typTokenRatiorotbaserad: 'types/sqrt(tokens)',
    enkelNominalkvot: 'Counts(NN) / Counts(VB)',
    fullNominalkvot: 'Counts(NN + PP + PC) / Counts(VB + AB + PN)',

    bilogarithmTtr: 'In(tokens) / In(types)',
    rootTtr: 'tokens / sqrt(types)',
    colemanLiauIndex: 'Coleman Liau Index',
    fleschReadingEase: 'Flesch Reading Ease',
    fleschKincaidGradeLevel: 'Flesch Kincaid Grade level',
    automatedReadabilityIndex: 'Automated Readability Index',
    smog: 'SMOG',

    a1LemmaIncsc: 'Incidence score for A1 words in sentences',
    a2LemmaIncsc: 'Incidence score for A2 words in sentences',
    b1LemmaIncsc: 'Incidence score for B1 words in sentences',
    b2LemmaIncsc: 'Incidence score for B2 words in sentences',
    c1LemmaIncsc: 'Incidence score for C1 words in sentences',
    c2LemmaIncsc: 'Incidence score for C2 words in sentences',
    difficultWordIncsc: 'Incidence score for words whose CEFR levels above B1',
    difficultNounOrVerbIncsc: 'Incidence score for nouns or verbs whose CEFR levels above B1',
    outOfKellyListIncsc: 'Incidence score for words out of KELLY-list',
    kellyLogFrequency: 'Average for logarithem of relative frequency',

    verbform: 'Incidence score for specific verb form to verbs',
    posPos: 'Incidence score for two parts of speech',
    subposAll: 'Incidence score for a sub part-of-speech',
    posAll: 'Incidence score for a part-of-speech',
    posMultipos: 'Incidence score for a part-of-speech to multiple parts-of-speech',
    multiposMultipos: 'Incidence score for multiple parts-of-speech to multiple parts-of-speech',

    posAll_adjIncsc: 'Incidence score for adjectives',
    posAll_advIncsc: 'Incidence score for adverbs',
    posAll_nounIncsc: 'Incidence score for nouns',
    posAll_partIncsc: 'Incidence score for particles',
    posAll_punctIncsc: 'Incidence score for punctuations',
    posAll_sconjIncsc: 'Incidence score for subordinating conjunctions',
    posAll_verbIncsc: 'Incidence score for verbs',

    posPos_nounToVerb: 'Incidence score for nouns to verbs',
    posPos_pronToNoun: 'Incidence score for pronouns to nouns',
    posPos_pronToPrep: 'Incidence score for pronouns to prepositions',
  
    'subposAll_s-verbIncsc': 'Incidence score for s-verbs',
    subposAll_neuterGenderNounIncsc: 'Incidence score for nouns whose gender is neuter',

    verbform_modalVerbToVerb: 'Incidence score for modal verbs to verbs',
    verbform_presentParticipleToVerb: 'Incidence score for present participles to verbs',
    verbform_pastParticipleToVerb: 'Incidence score for past participles to verbs',
    verbform_presentVerbToVerb: 'Incidence score for present verbs to verbs',
    verbform_pastVerbToVerb: 'Incidence score for past verbs to verbs',
    verbform_supineVerbToVerb: 'Incidence score for supine verbs to verbs',
    verbform_sVerbToVerb: 'Incidence score for s-verbs to verbs',

    posMultipos_adjVariation: 'Incidence score for adjectives to (ADJ + ADV + NOUN + VERB)',
    posMultipos_advVariation: 'Incidence score for adverbs to (ADJ + ADV + NOUN + VERB)',
    posMultipos_nounVariation: 'Incidence score for nouns to (ADJ + ADV + NOUN + VERB)',
    posMultipos_verbVariation: 'Incidence score for verbs to (ADJ + ADV + NOUN + VERB)',

    multiposMultipos_cconjSconjIncsc: 'Incidence score for conjunctions and subordinating conjunctions',
    multiposMultipos_functionalTokenIncsc: 'Incidence score for functional tokens',
    'multiposMultipos_lexToNon-lex': 'Incidence score for lexical tokens to non-lexical tokens',
    multiposMultipos_lexToToken: 'Incidence score for lexical tokens',
    multiposMultipos_nominalRatio: 'Incidence score for nominal ratio',
    multiposMultipos_relIncsc: 'Incidence score for relative and interrogative words',

    modalVerbToVerb: 'Incidence score for modal verbs to verbs',
    presentParticipleToVerb: 'Incidence score for present participles to verbs',
    pastParticipleToVerb: 'Incidence score for past participles to verbs',
    presentVerbToVerb: 'Incidence score for present verbs to verbs',
    pastVerbToVerb: 'Incidence score for past verbs to verbs',
    supineVerbToVerb: 'Incidence score for supine verbs to verbs',
    sVerbToVerb: 'Incidence score for s-verbs to verbs',

    nounToVerb: 'Incidence score for nouns to verbs',
    pronToNoun: 'Incidence score for pronouns to nouns',
    pronToPrep: 'Incidence score for pronouns to prepositions',

    sVerbIncsc: 'Incidence score for s-verbs',
    neuterGenderNounIncsc: 'Incidence score for nouns whose gender is neuter',

    adjIncsc: 'Incidence score for adjectives',
    advIncsc: 'Incidence score for adverbs',
    nounIncsc: 'Incidence score for nouns',
    partIncsc: 'Incidence score for particles',
    punctIncsc: 'Incidence score for punctuations',
    sconjIncsc: 'Incidence score for subordinating conjunctions',
    verbIncsc: 'Incidence score for verbs',

    adjVariation: 'Incidence score for adjectives to (ADJ + ADV + NOUN + VERB)',
    advVariation: 'Incidence score for adverbs to (ADJ + ADV + NOUN + VERB)',
    nounVariation: 'Incidence score for nouns to (ADJ + ADV + NOUN + VERB)',
    verbVariation: 'Incidence score for verbs to (ADJ + ADV + NOUN + VERB)',

    cconjSconjIncsc: 'Incidence score for conjunctions and subordinating conjunctions',
    functionalTokenIncsc: 'Incidence score for functional tokens',
    lexToNonLex: 'Incidence score for lexical tokens to non-lexical tokens',
    lexToToken: 'Incidence score for lexical tokens',
    nominalRatio: 'Incidence score for nominal ratio',
    relIncsc: 'Incidence score for relative and interrogative words',

    dependencyLength: 'The number of dependency arcs', // syntactic name
    dependencyArcsLongerThan5: 'The number of tokens whose dependency arcs are longer than 5', // syntactic features
    longestDependencyLength: 'The number of depdendency arcs with the longest dependency path', // syntactic features
    ratioOfRightDependencyArcs: 'The ratio between the number of right dependency arcs and all dependency arcs', // syntactic features
    ratioOfLeftDependencyArcs: 'The ratio between the number of left dependency arcs and all dependency arcs', // syntactic features
    modifierVariation: 'Incidence score for modifiers', // syntactic features
    preModifierIncsc: 'Incidence score for pre-modifiers', // syntactic features
    postModifierIncsc: 'Incidence score for post-modifiers', // syntactic features
    subordinateIncsc: 'Incidence score for subordinates', // syntactic features
    relativeClauseIncsc: 'Incidence score for relative clause', // syntactic features
    prepositionalComplementIncsc: 'Incidence score for prepositional complement', // syntactic features
  },
  topNavbar: {
    home: 'Home',
    addText: 'Add text',
    visualize: 'Visualize',
    statistics: 'Statistics',
    help: 'Help',
  },
  homePage: {
    resources: 'Resources',
    about: 'About',
    legacyVersion: 'Return to old Swegram',
    downloadManual: 'Download user manual',
    swegramIntro: 'SWEGRAM aims to provide a tool for text analysis in Swedish and English. You can upload one or several texts and annotate them at different linguistic levels with morphological and syntactic information. The annotated texts can then be used to extract statistics about the text properties with respect to text length, number of words, readability measures, part-of-speech, and much more.',
    svEntryText: 'Swedish texts',
    enEntryText: 'English texts',
    purpose: 'The SWEGRAM tool has been developed in collaboration between the Department of Scandinavian Languages and the Department of Linguistics and Philology at Uppsala University within the framework of the {0} project, which aims to make linguistic data available as primary research data for researchers within the Humanities and Social Sciences (HS) using advanced text and speech processing tools. SWEGRAM is now hosted and maintained by the Department of Linguistics, Stockholm University.',
    projectLeader: 'Project leader',
    projectLeaderContent: 'Beáta Megyesi, Department of Linguistics, SU',
    participant: 'Project participants',
    participantContent: 'Anne Palmér, Department of Scandinavian Languages, UU; Rex Ruan, Shifei Chen and Jesper Näsman, Department of Linguistics and Philology, UU',
    references: 'SWEGRAM is licensed under Creative Commons CC BY-SA, which allows you to freely use, share, copy, distribute, modify, and adapt the tool in various forms and formats for any purpose, including commercial use. However, you must provide appropriate credit to SWEGRAM in connection with any use, distribution, or modification. When using the tool, please reference it as follows:',
    getPDF: 'get pdf',
    article2024: 'SWEGRAM 2.0: Guidelines to Annotation and analysis of English and Swedish Texts.',
    reference2024: 'Megyesi, B. and Ruan, R. (2024) {0} Department of Linguistics, Stockholm University, Sweden.',
    reference2019: 'Megyesi, B., Palmér, A. & Näsman J. (2019) SWEGRAM -  Annotering och analys av svenska texter. Institutionen för lingvistik och filologi och Institutionen för nordiska språk, Uppsala universitet. [{0}]',
    reference2017: 'Näsman, J., Megyesi, B., & Palmér, A. (2017)  SWEGRAM  - A WebBased Tool for Automatic Annotation and Analysis of Swedish Texts. In Proceedings of 21st Nordic Conference on Computational Linguistics, Nodalida 2017. [{0}]',
    iconsCredit: 'Icons made by {0} from {1} is licensed by {2}',
    env: 'SWEGRAM is compatible with Chrome 58, Firefox 54 and Safari 10.',
  },
  statistics: {
    details: 'Details',
    name: 'Name',
    median: 'Median',
    mean: 'Mean',
    total: 'Total',
  },
  visualize: {
    markedToken: 'Marked Token',
    form: 'Form',
    norm: 'Norm',
    lemma: 'Lemma',
    upos: 'Upos',
    xpos: 'Xpos',
    feats: 'Feats',
    ufeats: 'Ufeats',
    head: 'Head',
    deprel: 'Deprel',
    deps: 'Deps',
    misc: 'Misc',
    dependencyLength: "Dependency's Length",
    stig: 'Stig',
  },
  textSelector: {
    selectTextsByMetadata: 'Select texts by metadata',
    selectAText: 'Select a text',
    pleaseSelectAText: 'Please select a text',
    download: 'Download',
    annotatedTextFile: 'Annotated Text File',
    statisticsSentenceLevel: 'Statistics (Sentence Level)',
    statisticsParagraphLevel: 'Statistics (Paragraph Level)',
    statisticsTextLevel: 'Statistics (Text Level)',
  },
  uploadPage: {
    annotateNewText: 'Annotate a new text',
    uploadMessage1: 'In order to annotate a new text, you can either | upload one or multiple (texts in format .doc, docx, .odt or .rtf, which are automatically converted into plain text), or | paste in a text.',
    uploadMessage2: 'For more information how metadata is handled, see | help | in menu.',
    textUploadButton: 'Upload a file',
    textPasteButton: 'Paste in a text',
  },
  uploadForm: {
    pasteBoxPlaceholder: 'Paste a text here to annotate',
    uploadTextFile: 'Upload Text File',
    back: 'Go back',
    annotate: 'Annotate',
    uploadPrompt: 'Click or drag file to select file. Then press Upload',
    upload: 'Upload',
    setting: 'Setting',
    tokenization: 'Tokenization',
    normalization: 'Normalization',
    posTaggingParsing: 'Pos Tagging/Parsing',
    annotatedTextPrompt: 'This is an annotated text',
    uploadSuccessMsg: 'Upload Success!',
    uploadFailedMsg: 'An error occured\n{0}',
    uploadErrNonText: 'Only plain text encoded in utf-8 is acceptable',
    uploadErrFileTooBig: 'Please upload a file less than 100MB',
    beforeUploadWarning: 'Upload a big file could take up to several hours, are you sure you want to continue?',
  },
  ...elementEN,
};

export default en;
