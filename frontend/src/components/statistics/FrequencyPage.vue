<script setup>
import { ref, computed, watch } from 'vue';
// NOTE: defineProps is a compiler macro provided by <script setup> and must NOT be imported from 'vue'.
// If you previously added `defineProps` to the import above, remove it to avoid the compiler error.
import { useRoute } from 'vue-router';
import { Document } from '@element-plus/icons-vue'
import axios from 'axios';
import SnippetFrequencyPanel from '@/components/statistics/FrequencyPanel.vue';
import SnippetFrequencyTypePosTable from '@/components/statistics/FrequencyPosTypeTable.vue';
import SnippetFrequencyPosTable from '@/components/statistics/FrequencyPosTable.vue';

const props = defineProps({
    tagset: { type: String, default: 'upos' },
    category: { type: String, default: 'form' },
    textsInfo: { type: Object, default: () => ({
        numberOfValidTexts: 0,
        validTexts: [],
        invalidTexts: [],
    }) },
    display: { type: Boolean, default: true },
    initialized: { type: Boolean, default: true },
});

const emit = defineEmits(['initialize']);

const route = useRoute();

const typePoS = ref('showType');
const showType = ref(true);
const typeList = ref([]); // a list with types
const typeViewList = ref([]); // a list with types filtered with pos tags based on typeList
const posList = ref([]);
const selectedPoS = ref([]);
const total = ref(0);
const loading = ref(false);
const numberOfTexts = ref(0);

const haveTextsNotIncluded = computed(() => {
    if (!props.textsInfo) return false;
    if (!props.textsInfo.invalidTexts) return false;
    return props.textsInfo.invalidTexts.length > 0;
});

watch(() => props.display, (newValue) => {
    // only work for the first time
    // otherwise use the same data
    if (newValue && !props.initialized) {
        emit('initialize', { type: 'frequency' });
        loadData();
    }
});

watch(() => props.category, () => {
    if (props.display) {
        loadData();
    }
});
watch(() => props.tagset, () => {
    if (props.display) {
        loadData();
    }
});
watch(() => props.textsInfo, () => {
    if (props.display) {
        loadData();
    }
});

async function loadData() {
    loading.value = true;
    try {
        await fetchData();
    } finally {
        loading.value = false;
    }
}

async function fetchData() {
    if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
    }
    const lang = route.params.toolVersion;
    const dataURL = `/api/frequencies/${props.category}/${props.tagset}/`;
    const response = await axios.post(dataURL, {
        texts: JSON.parse(localStorage.textList),
        lang,
    });
    const { data } = response;
    numberOfTexts.value = data.number_of_texts;
    // source list from backend
    const rawTypeList = data[`${props.category}_pos`] || [];
    total.value = rawTypeList.reduce((a, b) => a + b.count, 0);
    typeList.value = rawTypeList.map((e, i) => ({
        index: i + 1,
        token: e[props.category],
        pos: e.pos,
        frequency: e.count,
        ratio: (Math.round((e.count / total.value) * 10000) / 100).toString().concat(' %'),
    }));
    typeViewList.value = typeList.value.slice();
    posList.value = (data.pos_list || []).map((e, i) => ({
        index: i + 1,
        pos: e[0],
        frequency: e[1],
        ratio: (Math.round((e[1] / total.value) * 10000) / 100).toString().concat(' %'),
        model: true,
    }));
    selectedPoS.value = Array.from(new Set(posList.value.map((e) => e.pos)));
}

function getPercentage(n) {
    return (Math.round((n / total.value) * 10000) / 100).toString().concat(' %');
}

function getTypePoS(value) {
    showType.value = value === 'showType';
}

function handleTokenDeleteClick(value) {
    const { i, f, p } = value;
    total.value -= f;
    typeList.value = typeList.value.filter((typeElement) => typeElement.index !== i);
    typeList.value = typeList.value.map((typeElement, index) => ({
        ...typeElement,
        ratio: getPercentage(typeElement.frequency),
        index: index + 1,
    }));
    // update posList with its ratio and frequency
    posList.value = posList.value.map((posElement) => ({
        ...posElement,
        frequency: posElement.pos === p
            ? posElement.frequency - f
            : posElement.frequency,
        ratio: posElement.pos === p
            ? getPercentage(posElement.frequency - f)
            : getPercentage(posElement.frequency),
    }));
    updatePoSList();
    // update typeViewList
    updateTypeViewList();
}

function handlePoSSwitch(value) {
    const { state, pos, f } = value;
    if (state) {
        if (pos === 'ALL') {
            selectedPoS.value = Array.from(new Set(posList.value.map((e) => e.pos)));
            posList.value = posList.value.map((p) => ({
                ...p,
                model: true,
            }));
            total.value = typeList.value.reduce((a, b) => a + b.frequency, 0);
        } else {
            selectedPoS.value.push(pos);
            total.value += f;
        }
    } else if (pos === 'ALL') {
        selectedPoS.value = [];
        posList.value = posList.value.map((p) => ({
            ...p,
            model: false,
        }));
        total.value = 0;
    } else {
        selectedPoS.value = selectedPoS.value.filter((p) => p !== pos);
        total.value -= f;
    }
    updateTypeViewList();
}

function updateTypeViewList() {
    // filter out types by pos tags
    typeViewList.value = typeList.value.filter(
        (typeElement) => selectedPoS.value.includes(typeElement.pos),
    );
    // re-index the types
    typeViewList.value = typeViewList.value.map((e, index) => ({
        ...e,
        index: index + 1,
        ratio: getPercentage(e.frequency),
    }));
}

function updatePoSList() {
    // filter out pos if frequency is 0
    posList.value = posList.value.filter((posElement) => posElement.frequency > 0);
    // sort posList after its frequency
    posList.value.sort((a, b) => b.frequency - a.frequency);
    // re-index after sorting
    posList.value = posList.value.map((posElement, index) => ({
        ...posElement,
        index: index + 1,
    }));
}
</script>

<template>
  <div class="frequency-container">
    <template v-if="numberOfTexts > 0">
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
      <div
        v-if="posList.length > 0"
      >
        <snippet-frequency-panel
          :data-list="posList"
          :type-pos="typePoS"
          :tagset="tagset"
          :category="category"
          @switchPos="handlePoSSwitch"
          @changeShowType="getTypePoS"
        />
        <div
          v-show="showType"
        >
          <el-row>
            <snippet-frequency-type-pos-table
              :data-list="typeViewList"
              :tagset="tagset"
              :category="category"
              @deleteToken="handleTokenDeleteClick"
            />
          </el-row>
        </div>
        <div
          v-show="!showType"
        >
          <snippet-frequency-pos-table
            :data-list="posList"
            :tagset="tagset"
            @switchPoS="handlePoSSwitch"
          />
        </div>
      </div>
    </template>
    <template v-else>
      <el-empty description="There is no valid text selected." />
    </template>
  </div>
</template>

<style scoped>
.frequency-container {
  display: block;
}

.el-radio {
  display: block;
  margin: 50px 10px 0 10px;
}

.el-button {
  margin: 0 10px 0 10px;
}

</style>
