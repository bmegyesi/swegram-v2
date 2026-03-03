<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { Document } from '@element-plus/icons-vue'
import axios from 'axios';
import SnippetsList from '@/components/statistics/SnippetsList.vue';

const props = defineProps({
    level: { type: String, default: 'text', required: true },
    totalItems: { type: Number, default: null },
    textsInfo: {
        type: Object,
        default: () => ({
            numberOfValidTexts: 0,
            validTexts: [],
            invalidTexts: [],
        }),
    },
    showFeature: { type: Boolean, default: false },
    showFeatureLevel: { type: Boolean, default: false },
});

const route = useRoute();

const showTable = ref(false);
const selectedSnippetIdx = ref(null);
const dataSnippets = ref([]);
const contentSnippets = ref([]);
const currentPage = ref(1);
const loadingStatisticsTable = ref(false);
const contentLoading = ref(false);

const haveTextsNotIncluded = computed(() => {
    const ti = props.textsInfo;
    if (!ti || !ti.invalidTexts) return false;
    return ti.invalidTexts.length > 0;
});

function loadStatistics() {
    contentLoading.value = true;
    fetchStatictis();
}

function fetchStatictis() {
    if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
    }
    const lang = route.params.toolVersion;
    const featsURL = `/api/features/${props.level}/${currentPage.value}`;

    axios
        .post(featsURL, {
            texts: JSON.parse(localStorage.textList),
            lang,
        })
        .then((response) => {
            dataSnippets.value = response.data.statistics;
            contentSnippets.value = response.data.content;
        })
        .finally(() => {
            contentLoading.value = false;
        });
}

function handleCurrentPage({ page }) {
    currentPage.value = page;
}

/* watchers */
watch(
    () => props.showFeature,
    (newVal) => {
        if (newVal && props.showFeatureLevel) {
            loadStatistics();
        }
    }
);

watch(
    () => props.showFeatureLevel,
    () => {
        loadStatistics();
    }
);

watch(
    () => props.level,
    () => {
        if (props.showFeature && props.showFeatureLevel) {
            loadStatistics();
        }
    }
);

watch(
    () => props.textsInfo,
    (newVal, oldVal) => {
        const validTextsChange =
            JSON.stringify(oldVal?.validTexts) !== JSON.stringify(newVal?.validTexts);
        if (props.showFeature && props.showFeatureLevel && validTextsChange) {
            loadStatistics();
        }
    }
);

watch(currentPage, () => {
    loadStatistics();
});

onMounted(() => {
    loadStatistics();
});
</script>

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
          <span><el-icon><Document /></el-icon></span>{{ text[1] }}
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
