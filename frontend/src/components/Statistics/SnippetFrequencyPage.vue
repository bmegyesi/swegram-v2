<template>
  <div
    v-loading="loading"
  >
    <div
      v-if="numberOfTexts > 0"
      class="frequency-container"
    >
      <div
        v-if="haveTextsNotIncluded"
      >
        <el-divider>Texts below are not included.</el-divider>
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
            <snippet-frequency-type-table
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
    </div>
    <div v-else>
      There is no valid text selected.
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import SnippetFrequencyPanel from './SnippetFrequencyPanel.vue';
import SnippetFrequencyTypeTable from './SnippetFrequencyTypeTable.vue';
import SnippetFrequencyPosTable from './SnippetFrequencyPosTable.vue';

export default {
  components: {
    SnippetFrequencyPanel,
    SnippetFrequencyTypeTable,
    SnippetFrequencyPosTable,
  },
  props: {
    tagset: {
      type: String,
      default: 'upos',
      required: true,
    },
    category: {
      type: String,
      default: 'form',
      required: true,
    },
    textsInfo: {
      type: Object,
      default: () => ({
        numberOfValidTexts: 0,
        validTexts: () => [],
        invalidTexts: () => [],
      }),
      required: false,
    },
    display: {
      type: Boolean,
      default: true,
      required: false,
    },
    initialized: {
      type: Boolean,
      default: true,
      required: false,
    },
  },
  data() {
    return {
      typePoS: 'showType',
      showType: true,
      typeList: [], // a list with types
      typeViewList: [], // a list with types filtered with pos tags based on typeList
      posList: [],
      selectedPoS: [],
      total: 0,
      loading: false,
      numberOfTexts: 0,
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
    display(newValue) {
      // only work for the first time
      // otherwise use the same data
      if (newValue && !this.initialized) {
        this.$emit('initialize', { type: 'frequency' });
        this.loadData();
      }
    },
    category() {
      if (this.$props.display) {
        this.loadData();
      }
    },
    tagset() {
      if (this.$props.display) {
        this.loadData();
      }
    },
    textsInfo() {
      if (this.$props.display) {
        this.loadData();
      }
    },
  },

  methods: {
    loadData() {
      this.loading = true;
      this.fetchData();
    },
    fetchData() {
      if (!localStorage.textList) {
        localStorage.setItem('textList', JSON.stringify({}));
      }
      const lang = this.$route.params.toolVersion;
      const dataURL = `/api/frequencies/${this.$props.category}/${this.$props.tagset}/`;
      axios
        .post(dataURL, {
          texts: JSON.parse(localStorage.textList),
          lang,
        })
        .then((response) => {
          const { data } = response;
          this.numberOfTexts = data.number_of_texts;
          this.typeList = data[`${this.$props.category}_pos`];
          this.total = this.typeList.reduce((a, b) => a + b.count, 0);
          this.typeList = this.typeList.map((e, i) => ({
            index: i + 1,
            token: e[`${this.$props.category}`],
            pos: e.pos,
            frequency: e.count,
            ratio: (Math.round((e.count / this.total) * 10000) / 100).toString().concat(' %'),
          }));
          this.typeViewList = this.typeList;
          this.posList = data.pos_list.map((e, i) => ({
            index: i + 1,
            pos: e[0],
            frequency: e[1],
            ratio: (Math.round((e[1] / this.total) * 10000) / 100).toString().concat(' %'),
            model: true,
          }));
          this.selectedPoS = new Array(...new Set(this.posList.map((e) => e.pos)));
        })
        .then(() => {
          this.loading = false;
        });
    },
    getPercentage(n) {
      return (Math.round((n / this.total) * 10000) / 100).toString().concat(' %');
    },
    getTypePoS(value) {
      this.showType = value === 'showType';
    },
    handleTokenDeleteClick(value) {
      const { i, f, p } = value;
      this.total -= f;
      this.typeList = this.typeList.filter((typeElement) => typeElement.index !== i);
      this.typeList = this.typeList.map((typeElement, index) => ({
        ...typeElement,
        ratio: this.getPercentage(typeElement.frequency),
        index: index + 1,
      }));
      // update posList with its ratio and frequency
      this.posList = this.posList.map((posElement) => ({
        ...posElement,
        frequency: posElement.pos === p
          ? posElement.frequency - f
          : posElement.frequency,
        ratio: posElement.pos === p
          ? this.getPercentage(posElement.frequency - f)
          : this.getPercentage(posElement.frequency),
      }));
      this.updatePoSList();
      // update typeViewList
      this.updateTypeViewList();
    },
    handlePoSSwitch(value) {
      const { state, pos, f } = value;
      if (state) {
        if (pos === 'ALL') {
          this.selectedPoS = new Array(...new Set(this.posList.map((e) => e.pos)));
          this.posList = this.posList.map((p) => ({
            ...p,
            model: true,
          }));
          this.total = this.typeList.reduce((a, b) => a + b.frequency, 0);
        } else {
          this.selectedPoS.push(pos);
          this.total += f;
        }
      } else if (pos === 'ALL') {
        this.selectedPoS = [];
        this.posList = this.posList.map((p) => ({
          ...p,
          model: false,
        }));
        this.total = 0;
      } else {
        this.selectedPoS = this.selectedPoS.filter((p) => p !== pos);
        this.total -= f;
      }
      this.updateTypeViewList();
    },
    updateTypeViewList() {
      // filter out types by pos tags
      this.typeViewList = this.typeList.filter(
        (typeElement) => this.selectedPoS.includes(typeElement.pos),
      );
      // re-index the types
      this.typeViewList = this.typeViewList.map((e, index) => ({
        ...e,
        index: index + 1,
        ratio: this.getPercentage(e.frequency),
      }));
    },
    updatePoSList() {
      // filter out pos if frequency is 0
      this.posList = this.posList.filter((posElement) => posElement.frequency > 0);
      // sort posList after its frequency
      this.posList.sort((a, b) => b.frequency - a.frequency);
      // re-index after sorting
      this.posList = this.posList.map((posElement, index) => ({
        ...posElement,
        index: index + 1,
      }));
    },
  },
};
</script>

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
