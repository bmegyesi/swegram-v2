<template>
  <div class="container">
    <div class="left-container">
      <div class="text-selectors-section">
        <h5>Select text</h5>
        <el-row class="text-selectors-container">
          <el-select class="text-selector" placeholder="Select text" multiple collapse-tags :value="chosenTextIds"
            @change="handleTextIdSelectionChange">
            <el-option v-for="textId in textIDs" :key="textId[0]"
              :label="textId[1].split('.').slice(0, textId[1].split('.').length-1).join('.')" :value="textId[0]">
              <div class="textid-row-container">
                <span>
                  {{ textId[1]
                  .split('.')
                  .slice(0, textId[1].split('.').length-1).join('.')
                  }}
                </span>
                <i v-if="textId[0] !== SPECIAL_TEXTID_ALL_TEXT" class="el-icon-delete" size="mini" circle="true"
                  @click="handleTextDeleteClick(textId[0])" />
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
          <el-cascader :key="cascaderKey" v-show="metaData.length > 0" ref="metadata" v-model="chosenMetaData"
            class="text-selector" :options="options" :props="metaDataSelectorProps" placeholder="Select meta data"
            collapse-tags filterable>
            <template slot-scope="{ node, data }">
              <span v-if="!node.isLeaf"> {{ data.label }}({{ data.children.length }}) </span>
              <span v-else>
                {{ data.label.split('.')
                .slice(0, data.label.split('.').length-1)
                .join('.')
                }}
              </span>
            </template>
          </el-cascader>
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

<script>
import axios from 'axios';
import PosTypeSelector from './PosTypeSelector.vue';
import HighlightToken from '../Visualize/HighlightToken.vue';

export default {
  components: {
    PosTypeSelector,
    HighlightToken,
  },
  props: {
    showTagsetSelector: {
      type: Boolean,
      default: true,
      required: false,
    },
    showQuerySearch: {
      type: Boolean,
      default: true,
      required: false,
    },
    tokens: {
      type: Array,
      default: () => [],
      required: false,
    },
  },
  data() {
    return {
      SPECIAL_TEXTID_ALL_TEXT: -10000,
      metaDataSelectorProps: { multiple: true },
      options: [],
      metaData: [],
      chosenMetaData: [],
      textIDs: [],
      chosenTextIds: [],
      cascaderKey: 0,
    };
  },
  watch: {
    options() {
      this.cascaderKey += 1;
    },
    chosenTextIds(newValues) {
      this.chosenMetaData = this.metaData.filter((meta) => newValues.includes(meta[2]));
      this.postTextIdChange();
    },
    chosenMetaData(newValues, oldValues) {
      // if new nodes are added to the cascader
      if (newValues.length > oldValues.length) {
        // since unable to compare two arrays as object,
        // we stringify them to make it comparable
        const values = oldValues.map((value) => JSON.stringify(value));
        const addedTextIds = newValues
          .filter((value) => !values.includes(JSON.stringify(value)))
          .map((valueId) => valueId[2]);
        this.chosenTextIds = [...new Set(this.chosenTextIds.concat(addedTextIds))];
        // if nodes are deleted from the cascader
      } else if (newValues.length < oldValues.length) {
        const values = newValues.map((value) => JSON.stringify(value));
        const removedTextIds = oldValues
          .filter((value) => !values.includes(JSON.stringify(value)))
          .map((valueId) => valueId[2]);
        this.chosenTextIds = this.chosenTextIds
          .filter((textId) => !removedTextIds.includes(textId));
      }
    },
    textIDs(newValue) {
      if (newValue.length === 1) {
        if (newValue[0][0] === this.SPECIAL_TEXTID_ALL_TEXT) {
          this.textIDs = [];
        }
      }
    },
  },
  mounted() {
    this.requestCandidateFilesList();
  },
  methods: {
    highlightTokens({ query, type }) {
      this.$emit('querySearch', ({ query, type }));
    },
    handleTagSetChange(tagset) {
      this.$emit('tagSetChange', { newTagset: tagset.newTagset });
    },
    handleTypeSetChange(typeset) {
      this.$emit('typeSetChange', { newTypeset: typeset.newTypeset });
    },
    removeText(textId) {
      const lang = this.$route.params.toolVersion;
      const textList = JSON.parse(localStorage.textList);
      textList[lang] = textList[lang].filter((text) => (
        text.fields.text_id !== textId
      ));
      localStorage.setItem('textList', JSON.stringify(textList));
    },
    removeMetadata(textId) {
      const lang = this.$route.params.toolVersion;
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
      this.options.filter((option) => {
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
      this.options = filteredOptions;
    },
    async handleTextDeleteClick(textId) {
      await axios.delete(`/api/text/${textId}`);
      this.textIDs = this.textIDs.filter((text) => text[0] !== textId);
      this.chosenTextIds = this.chosenTextIds.filter((text) => text !== textId);
      this.metaData = this.metaData.filter((meta) => meta[2] !== textId);
      this.removeText(textId);
      this.removeMetadata(textId);
      // this.requestCandidateFilesList(); // include texts without metadata
      // this.getMetadata();
    },
    requestCandidateFilesList() {
      this.$emit('pageLoading', { loading: true });
      const lang = this.$route.params.toolVersion;
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
          if (response.data.text_ids.length > 0) {
            this.textIDs = [[this.SPECIAL_TEXTID_ALL_TEXT, 'All text.']].concat(response.data.text_ids);
            this.options = response.data.options;
            this.options.forEach((option) => {
              option.children.forEach((child) => {
                child.children.forEach((c) => {
                  this.metaData = this.metaData.concat([
                    [option.value, child.value, c.value],
                  ]);
                });
              });
            });
          } else {
            this.textIDs = [];
          }
          this.chosenTextIds = response.data.selected_text_ids;
        })
        .then(() => {
          this.$emit('pageLoading', { loading: false });
        });
    },
    handleTextIdSelectionChange(newTextIds) {
      if (newTextIds.includes(this.SPECIAL_TEXTID_ALL_TEXT)) {
        this.chosenTextIds = this.textIDs
          .filter((textId) => textId[0] !== this.SPECIAL_TEXTID_ALL_TEXT)
          .map((textId) => textId[0]);
      } else {
        this.chosenTextIds = [].concat(newTextIds);
      }
    },
    async postTextIdChange() {
      const lang = this.$route.params.toolVersion;
      const entries = this.textIDs
        .filter((textId) => textId[0] !== -10000)
        .map((i) => [i[0], this.chosenTextIds.includes(i[0])]);
      axios
        .put('/api/states/', {
          textStates: Object.fromEntries(entries),
          texts: JSON.parse(localStorage.textList)[lang],
        });
      this.$emit('textidchange', this.textIDs.filter((t) => this.chosenTextIds.includes(t[0])));
    },
  },
};
</script>

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
