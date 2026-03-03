<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { Download } from '@element-plus/icons-vue'

import axios from 'axios';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import TextSelector from '@/components/utils/TextSelector.vue';
import { ENGLISH_FEATURES, SWEDISH_FEATURES } from '@/components/lib/FeatureList';

const route = useRoute();

const downloadType = ref(['texts']);
const downloadDisabled = ref(false);
const showStatisticsArgs = ref(false);
const selectedTextIds = ref([]);
const levels = ref(['text', 'para', 'sent']);
const overviewOrDetail = ref(['overview', 'detail']);
const outputForm = ref('.txt');
const tooltipMsg = ref('');
const tooltipDisabled = ref(false);

const loadingTextSelection = ref(false);

const featureList = ref(SWEDISH_FEATURES);
const chosenFeatures = ref([]);

watch(downloadType, (newValue) => {
    if (newValue.includes('statistics')) {
        showStatisticsArgs.value = true;
        watchDownloadButton();
    } else {
        showStatisticsArgs.value = false;
        watchDownloadButton();
    }
});

watch(selectedTextIds, () => {
    watchDownloadButton();
});

watch(levels, () => {
    watchDownloadButton();
});

watch(overviewOrDetail, () => {
    watchDownloadButton();
});

onMounted(() => {
    let features;
    if (route.params.toolVersion === 'en') {
        features = ENGLISH_FEATURES;
    } else {
        features = SWEDISH_FEATURES;
    }
    featureList.value = features;
    features.options.forEach((feature) => {
        const aspectValue = feature.value;
        feature.children.forEach((child) => {
            const featureValue = child.value;
            if (child.children) {
                child.children.forEach((subChild) => {
                    chosenFeatures.value.push([aspectValue, featureValue, subChild.value]);
                });
            } else {
                chosenFeatures.value.push([aspectValue, featureValue]);
            }
        });
    });
});

function getFeatureName(feature) {
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
}

function handlePageLoading({ loading }) {
    loadingTextSelection.value = loading;
}

function watchDownloadButton() {
    tooltipDisabled.value = false;
    downloadDisabled.value = false;
    if (showStatisticsArgs.value) {
        if (selectedTextIds.value.length === 0) {
            tooltipMsg.value = 'No text is selected.';
        } else if (overviewOrDetail.value.length === 0) {
            tooltipMsg.value = 'Overview or|and detail is not chosen.';
        } else if (levels.value.length === 0) {
            tooltipMsg.value = 'Linguistic level(s) is not chosen.';
        } else {
            tooltipDisabled.value = true;
            downloadDisabled.value = false;
        }
    } else if (downloadType.value.length === 0) {
        tooltipMsg.value = 'Select annotated texts or|and statistics to be downloaded';
    } else if (selectedTextIds.value.length > 0 && !showStatisticsArgs.value) {
        tooltipDisabled.value = true;
        downloadDisabled.value = false;
    } else {
        tooltipMsg.value = 'No text is selected';
    }
}

function handleTextIdsChange(newTextIds) {
    selectedTextIds.value = newTextIds.map((t) => t[0]);
}

function fetchFeatures() {
    // get feature panel according to selected parameters (level, lang, overview|detail)
}

function handleDownloadCallback(filename) {
    console.log(filename);
    const downloadCallbackUrl = '/api/download/file/';
    axios({
        method: 'delete',
        data: { name: filename },
        url: downloadCallbackUrl,
    });
}

function handleDownloadEvent() {
    if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
    }
    if (!downloadDisabled.value && tooltipDisabled.value) {
        if (downloadType.value.includes('texts')) {
            const textDownloadURL = '/api/download/texts/';
            axios({
                method: 'post',
                data: {
                    outputForm: outputForm.value,
                    texts: JSON.parse(localStorage.textList),
                    lang: route.params.toolVersion,
                },
                responseType: 'blob',
                url: textDownloadURL,
            })
                .then((response) => {
                    const blob = new Blob([response.data], { type: 'application/force-download' });
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = `text-file${outputForm.value}`;
                    link.click();
                    return response.headers.filename;
                })
                .then((filename) => {
                    handleDownloadCallback(filename);
                });
        }
        if (downloadType.value.includes('statistics')) {
            const statsDownloadURL = '/api/download/statistics/';
            axios({
                method: 'post',
                data: {
                    overviewOrDetail: overviewOrDetail.value,
                    levels: levels.value,
                    chosenFeatures: chosenFeatures.value,
                    featureList: featureList.value.options,
                    outputForm: outputForm.value,
                    texts: JSON.parse(localStorage.textList),
                    lang: route.params.toolVersion,
                },
                responseType: 'blob',
                url: statsDownloadURL,
            })
                .then((response) => {
                    const blob = new Blob([response.data], { type: 'application/force-download' });
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = `statistics-file${outputForm.value}`;
                    link.click();
                });
        }
    }
}
</script>

<template>
  <default-layout>
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
          <template #header>
            <div class="clearfix">Overview & Detail</div>
          </template>
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
          <template #header>
            <div class="clearfix">Choose level(s)</div>
          </template>
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
          <template #default="{ node, data: option }">
            <span>{{ option ? $t(`features.${getFeatureName(option.label)}`) : '' }}</span>
            <span v-if="option && !node.isLeaf"> ({{ option.children ? option.children.length : 0 }}) </span>
          </template>
        </el-cascader>
      </el-main>

      <el-main class="download-type">
        <h5>Output form</h5>
        <el-radio-group v-model="outputForm">
          <el-radio value=".txt">txt</el-radio>
          <el-radio value=".csv">csv</el-radio>
          <!-- <el-radio value=".xlsx" /> -->
        </el-radio-group>
      </el-main>

      <el-main>
        <el-tooltip :disabled="tooltipDisabled" class="item" effect="light" placement="left-start">
          <template #content>
            {{ tooltipMsg }}
          </template>
          <el-button :disabled="downloadDisabled" class="download-button" @click="handleDownloadEvent">
            <Download /> Download
          </el-button>
        </el-tooltip>
      </el-main>
    </el-container>
  </default-layout>
</template>

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
