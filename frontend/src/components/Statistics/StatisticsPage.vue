<template>
  <el-container
    v-loading="loadingTextSelection"
  >
    <el-header height="auto">
      <text-selector
        :show-tagset-selector="showTagset"
        :show-query-search="false"
        @textidchange="handleTextIdsChange"
        @tagSetChange="handleTagset"
        @typeSetChange="handleTypeset"
        @pageLoading="handlePageLoading"
      />
    </el-header>
    <el-main>
      <el-tabs
        v-model="showType"
        type="border-card"
        @tab-click="handleShowTagset"
      >
        <el-tab-pane
          label="Frequency"
          name="frequency"
        >
          <snippet-frequency-page
            :tagset="tagset"
            :category="category"
            :texts-info="currentTextsStats()"
            :display="showFrequency"
            :initialized="initializeFrequency"
            :initialize="handleInitialization"
          />
        </el-tab-pane>

        <el-tab-pane
          label="Length"
          name="length"
        >
          <snippet-length-page
            :tagset="tagset"
            :category="category"
            :texts-info="currentTextsStats()"
            :display="showLength"
            :initialized="initializeLength"
            @initialize="handleInitialization"
          />
        </el-tab-pane>

        <el-tab-pane
          label="Linguistic features"
          name="feature"
        >
          <div
            v-if="selectedTextIds.length > 0"
          >
            <el-tabs
              v-model="featureLevel"
              tab-position="left"
              @tab-click="handleShowFeatureLevel"
            >
              <el-tab-pane
                label="Text"
                name="text"
              >
                <snippet-statistics-panel
                  level="text"
                  :texts-info="textsStats.parsed"
                  :total-items="totalTextItems"
                  :show-feature="showFeature"
                  :show-feature-level="showTextFeature"
                />
              </el-tab-pane>
              <el-tab-pane
                label="Paragraph"
                name="para"
              >
                <snippet-statistics-panel
                  level="para"
                  :texts-info="textsStats.parsed"
                  :total-items="totalParaItems"
                  :show-feature="showFeature"
                  :show-feature-level="showParaFeature"
                />
              </el-tab-pane>
              <el-tab-pane
                label="Sentence"
                name="sent"
              >
                <snippet-statistics-panel
                  level="sent"
                  :texts-info="textsStats.parsed"
                  :total-items="totalSentItems"
                  :show-feature="showFeature"
                  :show-feature-level="showSentFeature"
                />
              </el-tab-pane>
            </el-tabs>
          </div>
          <div v-else>
            There is no valid text selected.
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script>
import axios from 'axios';
import TextSelector from '../Common/TextSelector.vue';
import SnippetStatisticsPanel from './SnippetStatisticsPanel.vue';
import SnippetFrequencyPage from './SnippetFrequencyPage.vue';
import SnippetLengthPage from './SnippetLengthPage.vue';

export default {
  components: {
    TextSelector,
    SnippetStatisticsPanel,
    SnippetFrequencyPage,
    SnippetLengthPage,
  },
  data() {
    return {
      showType: '',
      featureLevel: '',

      showFrequency: false,
      showLength: false,
      showFeature: false,
      showTagset: false,

      showSentFeature: false,
      showParaFeature: false,
      showTextFeature: false,

      initializeFrequency: false,
      initializeLength: false,

      loadingTextSelection: false,

      selectedTextIds: [],
      tagset: 'upos',
      category: 'form',
      level: 'text',
      textsStats: {
        tokenized: {},
        normalized: {},
        parsed: {},
      },
      totalTextItems: 0,
      totalParaItems: 0,
      totalSentItems: 0,
    };
  },
  watch: {
    selectedTextIds() {
      this.fetchTextsStats();
      this.initializeFrequency = false;
      this.initializeLength = false;
    },
  },
  mounted() {
    // this.fetchTextsStats();
  },
  methods: {
    handleInitialization({ type }) {
      if (type === 'length') {
        this.initializeLength = true;
      } if (type === 'frequency') {
        this.initializeFrequency = true;
      }
    },
    handlePageLoading({ loading }) {
      this.loadingTextSelection = loading;
    },
    fetchTextsStats() {
      if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
      }
      const lang = this.$route.params.toolVersion;
      const baseURL = '/get_text_stats/';
      axios
        .post(baseURL, {
          textList: JSON.parse(localStorage.textList),
          lang,
        })
        .then((response) => {
          const { data } = response;

          this.totalTextItems = data.total_text_items;
          this.totalParaItems = data.total_para_items;
          this.totalSentItems = data.total_sent_items;
          this.textsStats = Object.fromEntries(
            Object.keys(this.textsStats)
              .map((annotationType) => ([
                annotationType, {
                  numberOfValidTexts: data[annotationType].number_of_valid_texts,
                  validTexts: data[annotationType].valid_texts,
                  invalidTexts: data[annotationType].invalid_texts,
                },
              ]
              )),
          );
        });
    },
    currentTextsStats() {
      if (this.category === 'form') {
        return this.textsStats.tokenized;
      } if (this.category === 'norm') {
        return this.textsStats.normalized;
      } if (this.category === 'lemma') {
        return this.textsStats.parsed;
      }
      return {
        numberOfValidTexts: 0,
        validTexts: () => [],
        invalidTexts: () => [],
      };
    },
    handleTextIdsChange(newTextIds) {
      this.selectedTextIds = newTextIds.map((t) => t[0]);
    },
    handleShowTagset(obj) {
      if (obj.name === 'frequency') {
        this.showFrequency = true;
        this.showLength = false;
        this.showFeature = false;
        this.showTagset = true;
      } if (obj.name === 'length') {
        this.showFrequency = false;
        this.showLength = true;
        this.showFeature = false;
        this.showTagset = true;
      } if (obj.name === 'feature') {
        this.showFrequency = false;
        this.showLength = false;
        this.showFeature = true;
        this.showTagset = false;
      }
    },
    handleShowFeatureLevel(obj) {
      if (obj.name === 'sent') {
        this.showSentFeature = true;
        this.showParaFeature = false;
        this.showTextFeature = false;
      } if (obj.name === 'para') {
        this.showSentFeature = false;
        this.showParaFeature = true;
        this.showTextFeature = false;
      } if (obj.name === 'text') {
        this.showSentFeature = false;
        this.showParaFeature = false;
        this.showTextFeature = true;
      }
    },
    handleTagset(value) {
      this.tagset = value.newTagset.toLowerCase();
    },
    handleTypeset(value) {
      this.category = value.newTypeset.toLowerCase();
    },
  },
};
</script>

<style scoped>

.el-main {
  display: block;
}

.el-tabs {
  width: 100%;
}

</style>
