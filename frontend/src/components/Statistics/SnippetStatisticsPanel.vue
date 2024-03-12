<template>
  <div>
    <div
      v-if="haveTextsNotIncluded"
    >
      <el-divider>The selected texts below are not parsed.</el-divider>
      <el-container
        v-for="text in textsInfo.invalidTexts"
        :key="text[0]"
      >
        <div style="margin: 10px;">
          <span><i class="el-icon-document" /></span>{{ text[1] }}
        </div>
      </el-container>
      <el-divider />
    </div>
    <snippets-list
      :snippets="contentSnippets"
      :content-loading="contentLoading"
      :level="level"
      :total="totalItems"
      :data-snippets="dataSnippets"
      @currentPage="handleCurrentPage"
    />
  </div>
</template>

<script>
import axios from 'axios';
import SnippetsList from './SnippetsList.vue';

export default {
  components: {
    SnippetsList,
  },
  props: {
    level: {
      type: String,
      default: null,
      required: true,
    },
    totalItems: {
      type: Number,
      default: 0,
      required: false,
    },
    textsInfo: {
      type: Object,
      default: () => ({
        numberOfValidTexts: 0,
        validTexts: () => [],
        invalidTexts: () => [],
      }),
    },
    showFeature: {
      type: Boolean,
      default: false,
      required: false,
    },
    showFeatureLevel: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      showTable: false,
      selectedSnippetIdx: null,
      dataSnippets: [],
      contentSnippets: [],
      currentPage: 1,
      loadingStatisticsTable: false,

      contentLoading: false,
    };
  },
  computed: {
    haveTextsNotIncluded() {
      if (!this.$props.textsInfo) {
        return false;
      } if (!this.$props.textsInfo.invalidTexts) {
        return false;
      }
      return this.$props.textsInfo.invalidTexts.length > 0;
    },
  },
  watch: {
    showFeature(newValue) {
      if (newValue && this.$props.showFeatureLevel) {
        this.loadStatistics();
      }
    },
    showFeatureLevel() {
      this.loadStatistics();
    },
    level() {
      if (this.$props.showFeature && this.$props.showFeatureLevel) {
        this.loadStatistics();
      }
    },
    textsInfo(o, n) {
      const validTextsChange = JSON.stringify(o.validTexts) !== JSON.stringify(n.validTexts);
      if (this.$props.showFeature && this.$props.showFeatureLevel && validTextsChange) {
        this.loadStatistics();
      }
    },
    currentPage() {
      this.loadStatistics();
    },
  },
  mounted() {
    this.loadStatistics();
  },
  methods: {
    loadStatistics() {
      this.contentLoading = true;
      this.fetchStatictis();
    },
    fetchStatictis() {
      if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
      }
      const lang = this.$route.params.toolVersion;
      const featsURL = `/api/features/${this.$props.level}/${this.currentPage}`;

      axios
        .post(featsURL, {
          texts: JSON.parse(localStorage.textList),
          lang,
        })
        .then((response) => {
          this.dataSnippets = response.data.statistics;
          this.contentSnippets = response.data.content;
        })
        .then(() => {
          this.contentLoading = false;
        });
    },
    handleCurrentPage({ page }) {
      this.currentPage = page; // used for pagination
    },
  },
};
</script>
