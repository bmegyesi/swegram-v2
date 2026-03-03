<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import TextSelector from '@/components/utils/TextSelector.vue';
import SnippetPanel from '@/components/visualize/SnippetVisualization.vue';

const selectedTextIds = ref([]);
const textMetadata = ref([]);
const currentText = ref(null);
const currentTextParsed = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const currentSentences = ref([]);
const loadingCurrentSentences = ref(false);
const loadingTextSelection = ref(false);
const totalItems = ref(0);
const tokens = ref([]); // used for highlighting the tokens
const query = ref('');
const type = ref('');

watch(currentText, (newValue) => {
    loadingCurrentSentences.value = true;
    currentPage.value = 1;
    checkCurrentTextParsed(newValue);
    fetchCurrentSentences();
  },
  { immediate: true }
);

watch(
  [currentPage, pageSize],
  () => {
    loadingCurrentSentences.value = true;
    fetchCurrentSentences();
  },
  { immediate: true }
)

async function checkCurrentTextParsed(newValue) {
    if (newValue !== '0' && newValue) {
        try {
            const response = await axios.get(`/api/text/${newValue}`);
            currentTextParsed.value = response.data.parsed;
        } catch (error) {
            console.log(error);
        }
    }
}

function handlePageLoading({ loading }) {
    loadingTextSelection.value = loading;
}

function handleTextIdsChange(newTextIds) {
    selectedTextIds.value = newTextIds;
}

function highlightTokens({ query: q, type: t }) {
    query.value = q;
    type.value = t;
    updateHighligted();
}

async function fetchCurrentSentences() {
    loadingCurrentSentences.value = true
    if (currentText.value !== null && currentText.value !== '0') {
        tokens.value = [];
        try {
            const response = await axios.get(`/api/text/${currentText.value}/${currentPage.value}/`);

            const data = response.data;

            currentSentences.value = data.current_sentences;
            textMetadata.value = data.metadata;
            totalItems.value = data.total_items;
            pageSize.value = data.page_size;
            currentSentences.value.forEach((sentence) => {
                tokens.value = tokens.value.concat(sentence.tokens);
            });
        } catch (e) {
            console.log(e);
        } finally {
            loadingCurrentSentences.value = false;
        }
    } else {
        loadingCurrentSentences.value = false;
    }
}

function updateHighligted() {
    const t = type.value;
    const q = query.value;
    currentSentences.value = currentSentences.value.map((sentence) => ({
        ...sentence,
        tokens: sentence.tokens.map((token) => {
            const field = token[t];
            const isMatch =
                field === q ||
                (t && t.endsWith && t.endsWith('feats') && q && field && typeof field.includes === 'function' && field.includes(q));
            return {
                ...token,
                highlight: isMatch ? 'highlight' : '',
            };
        }),
    }));
}
</script>

<template>
  <default-layout>
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
              <snippet-panel
                :snippets="currentSentences"
                :meta-data="textMetadata"
                :text-name="item[1]"
                :page-size="pageSize"
                :page-index="currentPage"
                :parsed="currentTextParsed">
              </snippet-panel>
              <el-pagination
                :hide-on-single-page="true"
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                layout="prev, pager, next, jumper"
                :total="totalItems" />
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </default-layout>
</template>

<style scoped>
.tooltips {
  margin-right: 30px;
  color: #909399;
}

.el-container {
  display: block;
}
</style>
