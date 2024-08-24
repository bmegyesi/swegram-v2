<template>
  <el-container>
    <el-header style="height: 240px;">
      <el-row>
        <div class="icons-container">
          <img
            src="../assets/swe-clarin-logo.png"
            height="110"
            width="160"
          >
          <!-- <img
            src="../assets/UU_logo_sv_84_transparent.png"
            height="125"
            width="125"
          > -->
        </div>
      </el-row>
      <el-row>
        <p class="link-container">
          <a href="..">
            <el-button type="plain">{{ $t('homePage.downloadManual') }}
              <i class="el-icon-collection" />
            </el-button>
          </a>
        </p>
      </el-row>
    </el-header>
    <el-container>
      <el-aside width="300px">
        <el-menu
          :default-active="activeIndex"
        >
          <el-menu-item
            index="1"
            style="height: 56px; line-height: 56px; vertical-algin:middle;"
            @click="goAnchor('introduction')"
          >
            Introduction
          </el-menu-item>
          <el-submenu
            index="2"
            @click="goAnchor('annotation')"
          >
            <template slot="title">
              <span>Annotation</span>
            </template>
            <el-menu-item-group>
              <el-menu-item
                index="2-1"
                @click="goAnchor('format')"
              >
                Format
              </el-menu-item>
              <el-submenu
                index="2-2"
                @click="goAnchor('annotationChain')"
              >
                <template slot="title">
                  <span>Annotation chain</span>
                </template>
                <el-menu-item-group>
                  <el-menu-item
                    index="2-2-1"
                    @click="goAnchor('formatting')"
                  >
                    Formatting
                  </el-menu-item>
                  <el-menu-item
                    index="2-2-2"
                    @click="goAnchor('tokenisationAndSentenceSegmentation')"
                  >
                    Tokenisation and sentence segmentation
                  </el-menu-item>
                  <el-menu-item
                    index="2-2-3"
                    @click="goAnchor('normalisationSpellingAndSeparatedCompoundWords')"
                  >
                    Normalisation, spelling and separated compound words
                  </el-menu-item>
                  <el-menu-item
                    index="2-2-4"
                    @click="goAnchor('lemmatisation')"
                  >
                    Lemmatisation
                  </el-menu-item>
                  <el-menu-item
                    index="2-2-5"
                    @click="goAnchor('partOfSpeechAnalysis')"
                  >
                    Part-of-speech analysis
                  </el-menu-item>
                  <el-menu-item
                    index="2-2-6"
                    @click="goAnchor('syntacticAnalysis')"
                  >
                    Syntactic analysis
                  </el-menu-item>
                </el-menu-item-group>
              </el-submenu>
              <el-menu-item
                index="2-3"
                @click="goAnchor('differentModelsForAutomaticAnalysis')"
              >
                Different models for automatic analysis
              </el-menu-item>
              <el-menu-item
                index="2-4"
                @click="goAnchor('correctionOfAutomaticAnalysis')"
              >
                Correction of automatic analysis
              </el-menu-item>
              <el-menu-item
                index="2-5"
                @click="goAnchor('saveYourAnnotatedFilesLocally')"
              >
                Save your annotated files locally and export them to Microsoft Excel
              </el-menu-item>
            </el-menu-item-group>
          </el-submenu>
          <el-submenu
            index="3"
            @hover="goAnchor('analysis')"
          >
            <template slot="title">
              <span>Analysis</span>
            </template>
            <el-menu-item-group>
              <el-menu-item
                index="3.1"
                @click="goAnchor('metadataAndFiltering')"
              >
                Metadata and filtering
              </el-menu-item>
              <el-submenu
                index="3.2"
                @click="goAnchor('statisticsAndQuantitativeMeasurements')"
              >
                <template
                  slot="title"
                >
                  <span
                    style="white-space: normal; line-height: 15px;"
                  >
                    Statistics and quantitative measurements
                  </span>
                </template>
                <el-menu-item-group>
                  <el-menu-item
                    index="3.2.1"
                    @click="goAnchor('generalStatistics')"
                  >
                    General statistics
                  </el-menu-item>
                  <el-menu-item
                    index="3.2.2"
                    @click="goAnchor('partOfSpeechStatistics')"
                  >
                    Part-of-speech statistics
                  </el-menu-item>
                  <el-submenu
                    index="3.2.3"
                    @click="goAnchor('readabilityMetrics')"
                  >
                    <template slot="title">
                      <span>Readability metrics</span>
                    </template>
                    <el-menu-item-group>
                      <el-menu-item
                        index="3.2.3.1"
                        @click="goAnchor('Lix')"
                      >
                        Lix
                      </el-menu-item>
                      <el-menu-item
                        index="3.2.3.2"
                        @click="goAnchor('typeTokenRatio')"
                      >
                        Type-token ratio
                      </el-menu-item>
                      <el-menu-item
                        index="3.2.3.3"
                        @click="goAnchor('Ovix')"
                      >
                        Ovix
                      </el-menu-item>
                      <el-menu-item
                        index="3.2.3.4"
                        @click="goAnchor('simpleNominalRatio')"
                      >
                        Simple nominal ratio
                      </el-menu-item>
                      <el-menu-item
                        index="3.2.3.5"
                        @click="goAnchor('fullNominalRatio')"
                      >
                        Full nominal ratio
                      </el-menu-item>
                    </el-menu-item-group>
                  </el-submenu>
                  <el-menu-item
                    index="3.2.4"
                    @click="goAnchor('frequencies')"
                  >
                    Frequencies
                  </el-menu-item>
                  <el-menu-item
                    index="3.2.5"
                    @click="goAnchor('morphologicalFeatures')"
                  >
                    Morpholoical features
                  </el-menu-item>
                  <el-submenu
                    index="3.2.6"
                    @click="goAnchor('syntacticFeatures')"
                  >
                    <template slot="title">
                      <span>Syntactic features</span>
                    </template>
                    <el-menu-item
                      index="3.2.6.1"
                      @click="goAnchor('syntacticFeaturesDependencyArcs')"
                    >
                      Syntactic features on basis of the number of dependency arcs
                    </el-menu-item>
                    <el-menu-item
                      index="3.2.6.2"
                      @click="goAnchor('syntacticFeaturesDependencyRelations')"
                    >
                      Syntactic features on basis of dependency relations
                    </el-menu-item>
                  </el-submenu>
                  <el-menu-item
                    index="3.2.7"
                    @click="goAnchor('lexicalFeatures')"
                  >
                    Lexical features
                  </el-menu-item>
                </el-menu-item-group>
              </el-submenu>
              <el-menu-item
                index="3.3"
                @click="goAnchor('visualiseTextsAndAnalysis')"
              >
                Visualise texts and analysis
              </el-menu-item>
              <el-menu-item
                index="3.4"
                @click="goAnchor('exportStatistics')"
              >
                Export statistics
              </el-menu-item>
            </el-menu-item-group>
          </el-submenu>
          <el-submenu
            index="4"
            @click="goAnchor('createYourOwnCorpus')"
          >
            <template slot="title">
              <span>
                Create your own corpus (text collection) with your own metadata
              </span>
            </template>
            <el-menu-item
              index="4.1"
              @click="goAnchor('exampleOfMetadataPreparation')"
            >
              Example of metadata preparation
            </el-menu-item>
          </el-submenu>
          <el-menu-item
            index="5"
            @click="goAnchor('aboutTheTool')"
          >
            About the tool
          </el-menu-item>
          <el-menu-item
            index="6"
            @click="goAnchor('references')"
          >
            References
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <h1 style="font-size: 40px; text-align: center;">
          Swegram Manual
        </h1>
        <div id="introduction">
          <h2>
            Introduction
          </h2>
          <p style="white-space: normal;">
            Swegram is a web-based tool that offers the ability to annotate and analyse Swedish and English texts. You can upload one or more texts and have them linguistically annotated with morphological and syntactic analysis. These linguistically annotated texts can then be used to perform quantitative linguistic analysis; for example, sentence lengths, total number of words, various readability metrics, PoS, frequency of PoS, base form and misspelt words.
          </p>
          <p>
            With the help of the tool, you can easily create your own linguistically annotated text collection, known as a corpus, and prepare statistics on the linguistic characteristics of your texts. The tool requires no knowledge of automated text processing nor any programming skills. Swegram is freely available to all users via the Swegram website at http://cl.lingfil.uu.se/swegram. Uploaded texts are not saved and are deleted from the server once your analysis is completed. This means that you can upload any texts you like without saving information about your identity or the texts you are working on. This does however prevent you from leaving the programme and returning to the same file later without re-uploading your work.
          </p>
          <p>
            In this manual, we describe how you can use the tool and its various functions on Swedish texts. Swegram also includes a help function that summarises the tool’s various components and functions. If you require any information missing from the manual or have any questions, please contact us: swegram@cl.lingfil.uu.se.
          </p>
        </div>
        <div id="annotation">
          <h2>Annotation</h2>
          <div id="format">
            <h3>Format</h3>
            <p>format content</p>
            <div id="annotationChain">
              <h3>Annotation chain</h3>
              <div id="formatting">
                <h4>Formatting</h4>
                <p>formatting content</p>
              </div>
              <div id="tokenisationAndSentenceSegmentation">
                <h4>Tokenisation and sentence segmentation</h4>
                <p>Tokensation content</p>
              </div>
              <div id="normalisationSpellingAndSeparatedCompoundWords">
                <h4>Normalisation, spelling and separated compound words</h4>
                <p>Normalisation content</p>
              </div>
              <div id="lemmatisation">
                <h4>Lemmatisation</h4>
                <p>Lemmatisation content</p>
              </div>
              <div id="partOfSpeechAnalysis">
                <h4>Part-of-speech analysis</h4>
                <p>part of speech analysis</p>
              </div>
              <div id="syntacticAnalysis">
                <h4>Syntactic analysis</h4>
                <p>Syntactic analysis content</p>
              </div>
            </div>
            <div id="differentModelsForAutomaticAnalysis">
              <h3>Different models for automatic analysis</h3>
              <p>Different models for automatic analysis content</p>
            </div>
            <div id="correctionOfAutomaticAnalysis">
              <h3>Correction of automatic analysis</h3>
              <p>Correction of automatic analysis content</p>
            </div>
            <div id="saveYourAnnotatedFilesLocally">
              <h3>Save your annotated files locally and export them to Microsoft Excel</h3>
              <p>microsoft content</p>
            </div>
          </div>
        </div>
        <div id="analysis">
          <h2>Analysis</h2>
          <div id="metadataAndFiltering">
            <h3>Metadata and filtering</h3>
            <p>metadata content</p>
          </div>
          <div id="statisticsAndQuantitativeMeasurements">
            <h3>Statistics and quantitative measurements</h3>
            <div id="generalStatistics">
              <h4>General statistics</h4>
              <p>general statistics content</p>
            </div>
            <div id="partOfSpeechStatistics">
              <h4>Part-of-speech statistics</h4>
              <p>part of speech statistics content</p>
            </div>
            <div id="readabilityMetrics">
              <h4>Readability metrics</h4>
              <div id="Lix">
                <h5>Lix</h5>
                <p>Lix content</p>
              </div>
              <div id="typeTokenRatio">
                <h5>Type-token ratio</h5>
                <p>ttr content</p>
              </div>
              <div id="Ovix">
                <h5>Ovix</h5>
                <p>Ovix content</p>
              </div>
              <div id="simpleNominalRatio">
                <h5>Simple nominal ratio</h5>
                <p>simple nominal ratio content</p>
              </div>
              <div id="fullNominalRatio">
                <h5>Full nominal ratio</h5>
                <p>Full nominal ratio content</p>
              </div>
            </div>
            <div id="frequencies">
              <h4>Frequencies</h4>
              <p>frequencies content</p>
            </div>
            <div id="morphologicalFeatures">
              <h4>Morphological features</h4>
              <p>morphological features contents</p>
            </div>
            <div id="syntacticFeatures">
              <h4>Syntactic features</h4>
              <div id="syntacticFeaturesDependencyArcs">
                <h5>Syntactic features on basis of the number of dependency arcs</h5>
                <p>3.2.6.1 features</p>
              </div>
              <div id="syntacticFeaturesDependencyRelations">
                <h5>Syntactic features on basis of dependency relations</h5>
                <p>3.2.6.2 features dependency relations</p>
              </div>
            </div>
            <div id="lexicalFeatures">
              <h4>Lexical features</h4>
              <p>Lexical feature content</p>
            </div>
          </div>
          <div id="visualiseTextsAndAnalysis">
            <h3>Visualise texts and analysis</h3>
            <p>Visulise texts and analysis contents</p>
          </div>
          <div id="exportStatistics">
            <h3>Export statistics</h3>
            <p>Export statistic features</p>
          </div>
        </div>
        <div id="createYourOwnCorpus">
          <h2>Create your own corpus (text collection) with your own metadata</h2>
          <div id="exampleOfMetadataPreparation">
            <h3>Example of metadata preparation</h3>
            <p>Example of metadata preparation features</p>
          </div>
        </div>
        <div id="aboutTheTool">
          <h2>About the tool</h2>
          <p>About the tool features</p>
        </div>
        <div id="references">
          <h2>References</h2>
          <p>Reference features</p>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default ({
  data() {
    return {
      activeIndex: '1',
    };
  },
  methods: {
    goAnchor(selector) {
      document.querySelector(`#${selector}`).scrollIntoView(true);
    },
  },
});
</script>

<style>
  /* it is necessary to write an independent style without scope to apply globally
  to make the following style work for the el-menu */
  .el-submenu__title {
    white-space: normal;
    line-height: 15px;
  }
</style>

<style scoped>

h2 {
  color: #303133;
}

.icons-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.icons-container img {
  margin: 20px;
}

.el-menu {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
}

.el-aside {
  position: relative;
  border: 2px black solid;
  margin-top: 20px;
  min-height: 50vh;
  max-height: 100vh;
  overflow: scroll;
}

.el-main {
  border: 2px black solid;
  margin-top: 20px;
  min-height: 50vh;
  max-height:100vh;
  overflow: scroll;
}

.el-menu-item {
  white-space: normal;
  line-height: 15px;
}

</style>
