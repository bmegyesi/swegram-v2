<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { Delete } from '@element-plus/icons-vue'
import axios from 'axios';
import PosTypeSelector from '@/components/utils/PosTypeSelector.vue';
import HighlightToken from '@/components/visualize/HighlightToken.vue';

const emit = defineEmits([
    'pageLoading',
    'querySearch',
    'tagSetChange',
    'typeSetChange',
    'textidchange',
]);

const props = defineProps({
    showTagsetSelector: { type: Boolean, default: true, required: false },
    showQuerySearch: { type: Boolean, default: true, required: false },
    tokens: { type: Array, default: () => [], required: false },
});

const route = useRoute();

const SPECIAL_TEXTID_ALL_TEXT = -10000;
const metaDataSelectorProps = { multiple: true };

const options = ref([]);
const metaData = ref([]);
const chosenMetaData = ref([]);
const textIDs = ref([]);
const chosenTextIds = ref([]);
const cascaderKey = ref(0);

function highlightTokens(payload) {
    emit('querySearch', ({ query: payload.query, type: payload.type }));
}

function handleTagSetChange(tagset) {
    emit('tagSetChange', { newTagset: tagset.newTagset });
}

function handleTypeSetChange(typeset) {
    emit('typeSetChange', { newTypeset: typeset.newTypeset });
}

function removeText(textId) {
    const lang = route.params.toolVersion;
    const textList = JSON.parse(localStorage.textList);
    textList[lang] = textList[lang].filter((text) => text.fields.text_id !== textId);
    localStorage.setItem('textList', JSON.stringify(textList));
}

function removeMetadata(textId) {
    const lang = route.params.toolVersion;
    const metadata = JSON.parse(localStorage.metadata);
    const filtered = {};
    Object.keys(metadata[lang]).filter((label) => {
        filtered[label] = {};
        const values = Object.keys(metadata[lang][label]).filter((value) => {
            const ids = metadata[lang][label][value].filter((t) => t[0] !== textId);
            if (ids.length !== 0) {
                filtered[label][value] = ids;
                return true;
            }
            return false;
        });
        if (values.length === 0) {
            delete filtered[label];
            return false;
        }
        return true;
    });
    metadata[lang] = filtered;
    localStorage.setItem('metadata', JSON.stringify(metadata));

    const filteredOptions = [];
    options.value.filter((option) => {
        const values = [];
        option.children.filter((child) => {
            const texts = child.children.filter((c) => c.value !== textId);
            if (texts.length !== 0) {
                const childComponent = { ...child, children: texts };
                values.push(childComponent);
                return true;
            }
            return false;
        });
        if (values.length !== 0) {
            const updatedOption = { ...option, children: values };
            filteredOptions.push(updatedOption);
            return true;
        }
        return false;
    });
    options.value = filteredOptions;
}

async function handleTextDeleteClick(textId) {
    await axios.delete(`/api/text/${textId}`);
    textIDs.value = textIDs.value.filter((text) => text[0] !== textId);
    chosenTextIds.value = chosenTextIds.value.filter((text) => text !== textId);
    metaData.value = metaData.value.filter((meta) => meta[2] !== textId);
    removeText(textId);
    removeMetadata(textId);
}

function requestCandidateFilesList() {
    emit('pageLoading', { loading: true });
    const lang = route.params.toolVersion;
    if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({ en: [], sv: [] }));
    }
    if (!localStorage.metadata) {
        localStorage.setItem('metadata', JSON.stringify({ en: {}, sv: {} }));
    }
    axios
        .put(`/api/texts/${lang}`, {
            texts: JSON.parse(localStorage.textList)[lang],
            metadata: JSON.parse(localStorage.metadata)[lang],
        })
        .then((response) => {
            metaData.value = [];
            if (response.data.text_ids.length > 0) {
                textIDs.value = [[SPECIAL_TEXTID_ALL_TEXT, 'All text.']].concat(response.data.text_ids);
                options.value = response.data.options;
                options.value.forEach((option) => {
                    option.children.forEach((child) => {
                        child.children.forEach((c) => {
                            metaData.value = metaData.value.concat([[option.value, child.value, c.value]]);
                        });
                    });
                });
            } else {
                textIDs.value = [];
            }
            chosenTextIds.value = response.data.selected_text_ids;
        })
        .then(() => {
            emit('pageLoading', { loading: false });
        });
}

function handleTextIdSelectionChange(newTextIds) {
    if (newTextIds.includes(SPECIAL_TEXTID_ALL_TEXT)) {
        chosenTextIds.value = textIDs.value
            .filter((textId) => textId[0] !== SPECIAL_TEXTID_ALL_TEXT)
            .map((textId) => textId[0]);
    } else {
        chosenTextIds.value = [].concat(newTextIds);
    }
}

function postTextIdChange() {
    const lang = route.params.toolVersion;
    const entries = textIDs.value
        .filter((textId) => textId[0] !== SPECIAL_TEXTID_ALL_TEXT)
        .map((i) => [i[0], chosenTextIds.value.includes(i[0])]);
    axios.put('/api/states/', {
        textStates: Object.fromEntries(entries),
        texts: JSON.parse(localStorage.textList)[lang],
    });
    emit('textidchange', textIDs.value.filter((t) => chosenTextIds.value.includes(t[0])));
}

watch(options, () => {
    cascaderKey.value += 1;
});

watch(
  () => chosenTextIds.value,
  (newValues) => {
    chosenMetaData.value = metaData.value.filter((meta) => newValues.includes(meta[2]));
    postTextIdChange();
  },
  { deep: true }
);

watch(chosenMetaData, (newValues, oldValues) => {
    if (!oldValues) return;
    if (newValues.length > oldValues.length) {
        const values = oldValues.map((value) => JSON.stringify(value));
        const addedTextIds = newValues
            .filter((value) => !values.includes(JSON.stringify(value)))
            .map((valueId) => valueId[2]);
        chosenTextIds.value = [...new Set(chosenTextIds.value.concat(addedTextIds))];
    } else if (newValues.length < oldValues.length) {
        const values = newValues.map((value) => JSON.stringify(value));
        const removedTextIds = oldValues
            .filter((value) => !values.includes(JSON.stringify(value)))
            .map((valueId) => valueId[2]);
        chosenTextIds.value = chosenTextIds.value.filter((textId) => !removedTextIds.includes(textId));
    }
});

watch(textIDs, (newValue) => {
    if (newValue.length === 1) {
        if (newValue[0][0] === SPECIAL_TEXTID_ALL_TEXT) {
            textIDs.value = [];
        }
    }
});

onMounted(() => {
    requestCandidateFilesList();
});
</script>

<template>
  <div class="container">
    <div class="left-container">
      <div class="text-selectors-section">
        <h5>Select text</h5>
        <el-row class="text-selectors-container">
          <el-select
            class="text-selector"
            placeholder="Select text"
            multiple
            collapse-tags
            v-model="chosenTextIds"
            @change="handleTextIdSelectionChange"
          >
            <el-option
              v-for="textId in textIDs"
              :key="textId[0]"
              :label="textId[1].split('.').slice(0, textId[1].split('.').length-1).join('.')"
              :value="textId[0]"
            >
              <div class="textid-row-container">
                <span>
                  {{ textId[1].split('.').slice(0, textId[1].split('.').length-1).join('.') }}
                </span>
                <el-icon
                  v-if="textId[0] !== SPECIAL_TEXTID_ALL_TEXT" @click="handleTextDeleteClick(textId[0])"
                >
                  <Delete />
                </el-icon>
              </div>
            </el-option>
          </el-select>
          <span v-show="metaData.length > 0">
            OR
          </span>
          <!-- there is a bug with clearable from element-ui
          it will not clear values from the v-models
          therefore, we do not implement attribute 'clearable'
          for cascader for now.
          -->
          <div v-show="metaData.length > 0">
            <el-cascader :key="cascaderKey" ref="metadata" v-model="chosenMetaData"
              class="text-selector" :options="options" :props="metaDataSelectorProps" placeholder="Select meta data"
              collapse-tags filterable>
              <template #default="{ node, data }">
                <span v-if="!node.isLeaf"> {{ data.label }}({{ data.children.length }})</span>
                <span v-else>
                  {{
                    data.label
                        .split('.')
                        .slice(0, data.label.split('.').length-1)
                        .join('.')
                  }}
                </span>
              </template>
            </el-cascader>
          </div>
        </el-row>
      </div>
      <pos-type-selector v-if="showTagsetSelector" @tagSetChange="handleTagSetChange"
        @typeSetChange="handleTypeSetChange" />
    </div>
    <div v-if="showQuerySearch" class="left-container">
      <h5>Search</h5>
      <highlight-token :tokens="tokens" @searchQuery="highlightTokens" />
    </div>
    <!-- <div v-show="chosenTextIds.length > 0" /> -->
  </div>
</template>

<style scoped>
.dropdown-link {
  cursor: pointer;
}

.hyperlink {
  text-decoration: none;
  color: #606266;
}

.container {
  background: #FFF;
  border: 1px solid #DCDFE6;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  padding-right: 60px;
}

.left-container {
  width: 70%;
}

.text-selectors-section {
  display: block;
}

.text-selectors-container {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 20px;
}

.text-selectors-container span {
  margin: 0 20px 0 20px;
}

.text-selector {
  width: 60%;
}

.textid-row-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prompt-title {
  width: 100%;
}

/* .pos-selector {
  margin-bottom: 10px;
} */
</style>
