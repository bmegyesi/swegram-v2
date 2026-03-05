<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { Document } from '@element-plus/icons-vue'
import axios from 'axios';
import SnippetLengthTable from '@/components/statistics/LengthTable.vue';

const props = defineProps({
  tagset: { type: String, default: 'upos' },
  category: { type: String, default: 'form' },
  textsInfo: {
    type: Object,
    default: () => ({
      numberOfValidTexts: 0,
      validTexts: [],
      invalidTexts: [],
    }),
  },
  display: { type: Boolean, default: true },
  initialized: { type: Boolean, default: true },
});

const emit = defineEmits(['initialize']);

const route = useRoute();
const dataList = ref([]); // data fetched from API
const theadList = ref([]); // table headers list fetched from API
const numberOfTexts = ref(0);
const loading = ref(false);

const haveTextsNotIncluded = computed(() => {
  if (!props.textsInfo) return false;
  if (!props.textsInfo.invalidTexts) return false;
  return props.textsInfo.invalidTexts.length > 0;
});

const fetchKey = computed(() => {
  return JSON.stringify({
    category: props.category,
    tagset: props.tagset,
    texts: props.textsInfo?.validTexts?.map(t => t[0]) ?? []
  })
})

watch(fetchKey, () => {
  loadData()
}, { immediate: true })


async function loadData() {
  loading.value = true;
  try {
    await fetchData();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function fetchData() {
  if (!localStorage.textList) {
    localStorage.setItem('textList', JSON.stringify({}));
  }
  const lang = route.params.toolVersion;
  const response = await axios.post(`/api/lengths/${props.category}/${props.tagset}/`, {
    texts: JSON.parse(localStorage.textList),
    lang,
  })

  dataList.value = response.data.length_list;
  theadList.value = response.data.pos_list;
  numberOfTexts.value = response.data.number_of_texts;
}

function handleColumnDelete(label) {
  theadList.value = theadList.value.filter((l) => l.label !== label);
  const labels = theadList.value.map((e) => e.label);
  dataList.value = dataList.value
    .map((e) => {
      const entries = Object.keys(e)
        .filter((p) => labels.includes(p))
        .map((p) => [p, e[p]]);
      const p = Object.fromEntries(entries);
      const pos = e.Length.data.find((element) => element.type === label);
      if (pos) {
        p.Length.data = p.Length.data.filter((element) => element.type !== label);
        p.Total.total -= pos.count;
      }
      return p;
    })
    .filter((element) => element.Total.total > 0);
}

function handleRowDelete(row) {
  const r = dataList.value.find((element) => element.Length.total === row);
  if (!r) return;
  const cols = r.Length.data
    .filter(
      (d) =>
        d.count === dataList.value.reduce((a, b) => a + b[d.type].total, 0),
    )
    .map((e) => e.type);
  cols.forEach((col) => handleColumnDeleteClick(col));
  dataList.value = dataList.value.filter((e) => e.Length.total !== row);
}

function handleColumnSortDown(label) {
  dataList.value = dataList.value.sort((a, b) => parseFloat(b[label].total) - parseFloat(a[label].total));
}

function handleColumnSortUp(label) {
  dataList.value = dataList.value.sort((a, b) => parseFloat(a[label].total) - parseFloat(b[label].total),);
}

</script>

<template>
  <div class="length-container" v-loading="loading">
    <div
      v-if="haveTextsNotIncluded"
    >
      <el-divider>Texts below are not included.</el-divider>
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
    <template v-if="numberOfTexts > 0">
      <el-row>
        <el-col
          :span="24"
        >
          <snippet-length-table
            :data-list="dataList"
            :thead-list="theadList"
            @delete-column="handleColumnDelete"
            @delete-row="handleRowDelete"
            @sort-up="handleColumnSortUp"
            @sort-down="handleColumnSortDown"
          />
        </el-col>
      </el-row>
    </template>
    <template v-else>
      There is no valid text selected.
    </template>
  </div>
</template>

<style scoped>

.length-container {
  display: block;
}

</style>
