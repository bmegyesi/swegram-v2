<template>
  <el-container v-loading="loadingTextSelection">
    <el-header height="auto">
      <text-selector :tokens="tokens" :show-tagset-selector="false" @textidchange="handleTextIdsChange"
        @querySearch="highlightTokens" @pageLoading="handlePageLoading" />
    </el-header>
    <el-main>
      <el-tabs v-model="currentText" type="card">
        <el-tab-pane v-for="item in selectedTextIds" :key="item[0]" :label="item[1].split('.')[0]"
          :name="item[0].toString()">
          <el-card v-loading="loadingCurrentSentences">
            <snippet-panel :snippets="currentSentences" :meta-data="textMetadata" :text-name="item[1]"
              :page-size="pageSize" :page-index="currentPage" :parsed="currentTextParsed" />
            <el-pagination :hide-on-single-page="true" :current-page.sync="currentPage" :page-size="10"
              layout="prev, pager, next, jumper" :total="totalItems" />
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>

<script>
import axios from 'axios';
import TextSelector from '../Common/TextSelector.vue';
import SnippetPanel from './SnippetVisualization.vue';

export default {
  components: {
    TextSelector,
    SnippetPanel,
  },
  data() {
    return {
      selectedTextIds: [],
      textMetadata: [],
      currentText: null,
      currentTextParsed: false,
      currentPage: 1,
      currentSentences: [],
      loadingCurrentSentences: false,
      loadingTextSelection: false,
      totalItems: null,
      pageSize: null,
      tokens: [], // used for highlighting the tokens
      query: '',
      type: '',
    };
  },
  watch: {
    // selectedTextIds() {
    //   // this.fetchSentences();
    // },
    currentText(newValue) {
      this.loadingCurrentSentences = true;
      this.currentPage = 1;
      this.checkCurrentTextParsed(newValue);
      this.fetchCurrentSentences();
    },
    currentPage() {
      this.loadingCurrentSentences = true;
      this.fetchCurrentSentences();
    },
  },
  methods: {
    checkCurrentTextParsed(newValue) {
      if (newValue !== '0' && newValue) {
        axios
          .get(`/api/text/${newValue}`)
          .then((response) => {
            this.currentTextParsed = JSON.parse(response.data)[0].fields.parsed;
          })
          .catch((error) => {
            console.log(error);
          });
      }
    },
    handlePageLoading({ loading }) {
      this.loadingTextSelection = loading;
    },
    handleTextIdsChange(newTextIds) {
      this.selectedTextIds = newTextIds;
    },
    handleCurrentPage({ page }) {
      this.currentPage = page;
    },
    highlightTokens({ query, type }) {
      this.query = query;
      this.type = type;
      this.updateHighligted();
    },
    fetchCurrentSentences() {
      if (this.currentText !== null && this.currentText !== '0') {
        this.tokens = [];
        axios
          .get(`/api/text/${this.currentText}/${this.currentPage}/`)
          .then((response) => {
            const { data } = response;
            this.currentSentences = data.current_sentences;
            this.textMetadata = data.metadata;
            this.totalItems = data.total_items;
            this.pageSize = data.page_size;

            this.currentSentences.forEach((sentence) => {
              this.tokens = this.tokens.concat(sentence.tokens);
            });
          })
          .then(() => {
            this.loadingCurrentSentences = false;
          });
      }
    },
    updateHighligted() {
      this.currentSentences = this.currentSentences
        .map((sentence) => ({
          ...sentence,
          tokens: sentence.tokens
            .map((token) => ({
              ...token,
              highlight: token[this.type] === this.query || (this.type.endsWith('feats') && this.query && (token[this.type].includes(this.query)))
                ? 'highlight'
                : '',
            })),
        }));
    },
  },
};
</script>

<style scoped>
.tooltips {
  margin-right: 30px;
  color: #909399;
}

.el-container {
  display: block;
}
</style>
