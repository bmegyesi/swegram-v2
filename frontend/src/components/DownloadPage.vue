<template>
  <el-container v-loading="loadingTextSelection">
    <el-main class="download-type">
      <h5>Export</h5>
      <el-checkbox-group v-model="downloadType">
        <el-checkbox label="texts">
          Annotated texts
        </el-checkbox>
        <el-checkbox label="statistics">
          Statistics
        </el-checkbox>
      </el-checkbox-group>
    </el-main>

    <el-header height="auto">
      <text-selector :show-tagset-selector="false" :show-query-search="false" @textidchange="handleTextIdsChange"
        @pageLoading="handlePageLoading" />
    </el-header>

    <el-main v-show="showStatisticsArgs">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          Overview & Detail
        </div>
        <el-checkbox-group v-model="overviewOrDetail">
          <el-checkbox label="overview">
            Overview
          </el-checkbox>
          <el-checkbox label="detail">
            Detail
          </el-checkbox>
        </el-checkbox-group>
      </el-card>
    </el-main>

    <el-main v-show="showStatisticsArgs">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          Choose level(s)
        </div>
        <el-checkbox-group v-model="levels">
          <el-checkbox label="text">
            Text
          </el-checkbox>
          <el-checkbox label="para">
            Paragraph
          </el-checkbox>
          <el-checkbox label="sent">
            Sentence
          </el-checkbox>
        </el-checkbox-group>
      </el-card>
    </el-main>

    <el-main v-show="showStatisticsArgs" class="feature-container">
      <h5>Specify features to be exported.</h5>
      <el-cascader ref="feature-selection" v-model="chosenFeatures" :options="featureList.options"
        :props="{ multiple: true }" placeholder="Select features" collapse-tags filterable>
        <template slot-scope="{ node, data }">
          <span>{{ $t(`features.${getFeatureName(data.label)}`) }}</span>
          <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
        </template>
      </el-cascader>
    </el-main>

    <el-main class="download-type">
      <h5>Output form</h5>
      <el-radio-group v-model="outputForm">
        <el-radio label=".txt" />
        <el-radio label=".csv" />
        <el-radio label=".xlsx" />
      </el-radio-group>
    </el-main>

    <el-main>
      <el-tooltip :disabled="tooltipDisabled" class="item" effect="light" placement="left-start">
        <div slot="content">
          {{ tooltipMsg }}
        </div>
        <el-button :disabled="downloadDisabled" class="download-button" @click="handleDownloadEvent">
          <span>Download</span>
          <i class="el-icon-download" />
        </el-button>
      </el-tooltip>
    </el-main>
  </el-container>
</template>

<script>
import axios from 'axios';
import TextSelector from './Common/TextSelector.vue';
import { ENGLISH_FEATURES, SWEDISH_FEATURES } from '../FeatureList';

export default {
  components: {
    TextSelector,
  },
  data() {
    return {
      downloadType: [],
      downloadDisabled: false,
      showStatisticsArgs: false,
      selectedTextIds: [],
      levels: [],
      overviewOrDetail: [],
      outputForm: '.txt',
      tooltipMsg: '',
      tooltipDisabled: false,

      loadingTextSelection: false,

      featureList: SWEDISH_FEATURES,
      chosenFeatures: [],
    };
  },
  watch: {
    downloadType(newValue) {
      if (newValue.includes('statistics')) {
        this.showStatisticsArgs = true;
        this.watchDownloadButton();
      } else {
        this.showStatisticsArgs = false;
        this.watchDownloadButton();
      }
      // if (newValue !== 'Statistics' || this.selectedTextIds.length === 0) {
      //   this.showStatistics = false;
      // } else {
      //   this.showStatistics = true;
      // }
    },
    selectedTextIds() {
      this.watchDownloadButton();
    },
    levels() {
      this.watchDownloadButton();
    },
    overviewOrDetail() {
      this.watchDownloadButton();
    },
  },
  mounted() {
    let features;
    if (this.$route.params.toolVersion === 'en') {
      features = ENGLISH_FEATURES;
    } else {
      features = SWEDISH_FEATURES;
    }
    this.featureList = features;
    features.options.forEach((feature) => {
      const aspectValue = feature.value;
      feature.children.forEach((child) => {
        const featureValue = child.value;
        if (child.children) {
          child.children.forEach((subChild) => {
            this.chosenFeatures.push([aspectValue, featureValue, subChild.value]);
          });
        } else {
          this.chosenFeatures.push([aspectValue, featureValue]);
        }
      });
    });
  },
  methods: {
    getFeatureName(feature) {
      const fn = feature
        .replace('(', '')
        .replace(')', '')
        .replace(' & ', ' ')
        .replace('-', ' ')
        .split(' ');
      const head = fn.slice(0, 1).join().toLowerCase();
      const tail = fn.slice(1)
        .map((w) => w[0].toUpperCase() + w.slice(1).toLowerCase());
      return head + tail.join('');
    },
    handlePageLoading({ loading }) {
      this.loadingTextSelection = loading;
    },
    watchDownloadButton() {
      this.tooltipDisabled = false;
      this.downloadDisabled = false;
      if (this.showStatisticsArgs) {
        if (this.selectedTextIds.length === 0) {
          this.tooltipMsg = 'No text is selected.';
        } else if (this.overviewOrDetail.length === 0) {
          this.tooltipMsg = 'Overview or|and detail is not chosen.';
        } else if (this.levels.length === 0) {
          this.tooltipMsg = 'Linguistic level(s) is not chosen.';
        } else {
          this.tooltipDisabled = true;
          this.downloadDisabled = false;
        }
      } else if (this.downloadType.length === 0) {
        this.tooltipMsg = 'Select annotated texts or|and statistics to be downloaded';
      } else if (this.selectedTextIds.length > 0 && !this.showStatisticsArgs) {
        this.tooltipDisabled = true;
        this.downloadDisabled = false;
      } else {
        this.tooltipMsg = 'No text is selected';
      }
    },
    handleTextIdsChange(newTextIds) {
      this.selectedTextIds = newTextIds.map((t) => t[0]);
    },
    fetchFeatures() {
      // get feature panel according to selected parameters (level, lang, overview|detail)
    },
    handleDownloadEvent() {
      if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
      }
      if (!this.downloadDisabled && this.tooltipDisabled) {
        if (this.downloadType.includes('texts')) {
          const textDownloadURL = '/download_text/';
          axios({
            method: 'post',
            data: {
              outputForm: this.outputForm,
              texts: JSON.parse(localStorage.textList),
              lang: this.$route.params.toolVersion,
            },
            responseType: 'blob',
            url: textDownloadURL,
          })
            .then((response) => {
              const blob = new Blob([response.data], { type: 'application/force-download' });
              const link = document.createElement('a');
              link.href = window.URL.createObjectURL(blob);
              // the name of downloaded text
              link.download = `text-file${this.outputForm}`;
              link.click();
            });
        } if (this.downloadType.includes('statistics')) {
          const statsDownloadURL = '/download_stats/';
          axios({
            method: 'post',
            data: {
              overviewOrDetail: this.overviewOrDetail,
              levels: this.levels,
              chosenFeatures: this.chosenFeatures,
              featureList: this.featureList.options,
              outputForm: this.outputForm,
              texts: JSON.parse(localStorage.textList),
              lang: this.$route.params.toolVersion,
            },
            responseType: 'blob',
            url: statsDownloadURL,
          })
            .then((response) => {
              const blob = new Blob([response.data], { type: 'application/force-download' });
              const link = document.createElement('a');
              link.href = window.URL.createObjectURL(blob);
              link.download = `statistics-file${this.outputForm}`;
              link.click();
            });
        }
      }
    },
  },
};
</script>

<style scoped>
.download-type {
  margin: 20px;
  border: 1px solid #DCDFE6;
}

.feature-container {
  margin: 20px;
  border: 1px solid #DCDFE6;
}

.el-alert {
  margin-top: 100px;
  height: 60vh;
  justify-content: center;
  background: #FFF;
  border: 1px solid #DCDFE6;
  display: flex;
  flex-direction: column;
  padding: 20px;
  padding-right: 60px;

}

.download-button {
  border: 1px solid #DCDFE6;
  float: right;
}

.download-setting {
  margin-top: 130px;
}

.el-cascader {
  margin-top: 20px;
}
</style>
