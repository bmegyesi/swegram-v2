<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import TextSelector from '@/components/utils/TextSelector.vue';
import SnippetStatisticsPanel from '@/components/statistics/SnippetStatisticsPanel.vue';
import SnippetFrequencyPage from '@/components/statistics/FrequencyPage.vue';
import SnippetLengthPage from '@/components/statistics/LengthPage.vue';

const route = useRoute();

// state
const isMobile = ref(false);
const showType = ref('frequency');
const featureLevel = ref('text');

const showFrequency = ref(true);
const showLength = ref(false);
const showFeature = ref(false);
const showTagset = ref(true);

const showSentFeature = ref(false);
const showParaFeature = ref(false);
const showTextFeature = ref(true);

const initializeFrequency = ref(false);
const initializeLength = ref(false);

const loadingTextSelection = ref(false);

const selectedTextIds = ref([]);
const tagset = ref('upos');
const category = ref('form');
const level = ref('text');

const textsStats = reactive({
    tokenized: {},
    normalized: {},
    parsed: {},
});

const totalTextItems = ref(0);
const totalParaItems = ref(0);
const totalSentItems = ref(0);

// computed
const tabPosition = computed(() => (isMobile.value ? 'top' : 'left'));

// watchers
watch(selectedTextIds, () => {
    fetchTextsStats();
    initializeFrequency.value = false;
    initializeLength.value = false;
});

// lifecycle
onMounted(() => {
    fetchTextsStats();
    checkMobile();
    window.addEventListener('resize', checkMobile);
});
onBeforeUnmount(() => {
    window.removeEventListener('resize', checkMobile);
});

// methods
function checkMobile() {
    isMobile.value = window.innerWidth < 768;
}

function handleInitialization({ type }) {
    if (type === 'length') {
        initializeLength.value = true;
    }
    if (type === 'frequency') {
        initializeFrequency.value = true;
    }
}

function handlePageLoading({ loading }) {
    loadingTextSelection.value = loading;
}

function fetchTextsStats() {
    if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
    }
    const lang = route.params.toolVersion;
    const baseURL = '/api/states/';
    axios
        .post(baseURL, {
            textList: JSON.parse(localStorage.textList),
            lang,
        })
        .then((response) => {
            const { data } = response;

            totalTextItems.value = data.total_text_items;
            totalParaItems.value = data.total_para_items;
            totalSentItems.value = data.total_sent_items;

            // update reactive textsStats properties
            Object.keys(textsStats).forEach((annotationType) => {
                const keyFromResponse = annotationType; // tokenized/normalized/parsed match response keys
                textsStats[annotationType] = {
                    numberOfValidTexts: data[keyFromResponse].number_of_valid_texts,
                    validTexts: data[keyFromResponse].valid_texts,
                    invalidTexts: data[keyFromResponse].invalid_texts,
                };
            });
        })
        .catch(() => {
            // keep it silent or add error handling as needed
        });
}

function currentTextsStats() {
    if (category.value === 'form') {
        return textsStats.tokenized;
    }
    if (category.value === 'norm') {
        return textsStats.normalized;
    }
    if (category.value === 'lemma') {
        return textsStats.parsed;
    }
    return {
        numberOfValidTexts: 0,
        validTexts: () => [],
        invalidTexts: () => [],
    };
}

function handleTextIdsChange(newTextIds) {
    selectedTextIds.value = newTextIds.map((t) => t[0]);
}

function handleShowTagset(obj) {
    if (obj.name === 'frequency') {
        showFrequency.value = true;
        showLength.value = false;
        showFeature.value = false;
        showTagset.value = true;
    }
    if (obj.name === 'length') {
        showFrequency.value = false;
        showLength.value = true;
        showFeature.value = false;
        showTagset.value = true;
    }
    if (obj.name === 'feature') {
        showFrequency.value = false;
        showLength.value = false;
        showFeature.value = true;
        showTagset.value = false;
    }
}

function handleShowFeatureLevel(obj) {
    if (obj.name === 'sent') {
        showSentFeature.value = true;
        showParaFeature.value = false;
        showTextFeature.value = false;
    }
    if (obj.name === 'para') {
        showSentFeature.value = false;
        showParaFeature.value = true;
        showTextFeature.value = false;
    }
    if (obj.name === 'text') {
        showSentFeature.value = false;
        showParaFeature.value = false;
        showTextFeature.value = true;
    }
}

function handleTagset(value) {
    tagset.value = value.newTagset.toLowerCase();
}

function handleTypeset(value) {
    category.value = value.newTypeset.toLowerCase();
}
</script>

<template>
  <default-layout>
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
              :initialize="handleInitialization"
            />
          </el-tab-pane>

          <el-tab-pane
            label="Linguistic features"
            name="feature"
          >
            <div>
              <div v-show="selectedTextIds.length > 0">
                <el-tabs
                  v-model="featureLevel"
                  :tab-position="tabPosition"
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
              <div v-show="selectedTextIds.length === 0">
                There is no valid text selected.
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </default-layout>
</template>

<style scoped>

.el-main {
  display: block;
}

.el-tabs {
  width: 100%;
}

</style>
