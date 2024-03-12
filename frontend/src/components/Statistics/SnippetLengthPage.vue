<template>
  <el-container v-loading="loading">
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
      v-if="numberOfTexts === 0"
    >
      There is no valid text selected.
    </div>
    <div
      v-else
    >
      <el-row>
        <el-col
          :span="24"
        >
          <snippet-length-table
            :data-list="dataList"
            :thead-list="theadList"
            @deleteColumn="handleColumnDeleteClick"
            @deleteRow="handleRowDeleteClick"
            @sortUp="handleColumnSortUp"
            @sortDown="handleColumnSortDown"
          />
        </el-col>
      </el-row>
    </div>
  </el-container>
</template>

<script>
import axios from 'axios';
import SnippetLengthTable from './SnippetLengthTable.vue';

export default {
  components: {
    SnippetLengthTable,
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
      default: false,
      required: false,
    },
    initialized: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      lengths: [],
      posList: [],
      dataList: [], // data fetched from API
      theadList: [], // table headers list fetched from API
      numberOfTexts: 0,
      loading: false,
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
        this.$emit('initialize', { type: 'length' });
        // this.initialized = true;
        this.loadData();
      }
    },
    tagset() {
      if (this.$props.display) {
        this.loadData();
      }
    },
    category() {
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
      axios
        .post(`/api/lengths/${this.$props.category}/${this.$props.tagset}/`, {
          texts: JSON.parse(localStorage.textList),
          lang,
        })
        .then((response) => {
          this.dataList = response.data.length_list;
          this.theadList = response.data.pos_list;
          this.numberOfTexts = response.data.number_of_texts;
        })
        .then(() => {
          this.loading = false;
        });
    },
    handleColumnDeleteClick(label) {
      this.theadList = this.theadList.filter((l) => l.label !== label);
      const labels = this.theadList.map((e) => e.label);
      this.dataList = this.dataList.map((e) => {
        const entries = Object.keys(e).filter((p) => labels.includes(p)).map((p) => [p, e[p]]);
        const p = Object.fromEntries(entries);
        const pos = e.Length.data.find((element) => element.type === label);
        if (pos) {
          p.Length.data = p.Length.data.filter((element) => element.type !== label);
          p.Total.total -= pos.count;
        }
        return p;
      }).filter((element) => element.Total.total > 0);
    },
    handleRowDeleteClick(row) {
      // check which columns (pos) have the only length related to the row
      const r = this.dataList.find((element) => element.Length.total === row);
      const cols = r.Length.data.filter(
        (d) => d.count === this.dataList.reduce(
          (a, b) => a + b[d.type].total, 0,
        ),
      ).map((e) => e.type);
      cols.forEach((col) => this.handleColumnDeleteClick(col));
      this.dataList = this.dataList.filter((e) => e.Length.total !== row);
    },
    handleColumnSortDown(label) {
      this.dataList = this.dataList.sort(
        (a, b) => parseFloat(b[label].total) - parseFloat(a[label].total),
      );
    },
    handleColumnSortUp(label) {
      this.dataList = this.dataList.sort(
        (a, b) => parseFloat(a[label].total) - parseFloat(b[label].total),
      );
    },
  },
};
</script>

<style scoped>

.el-container {
  display: block;
}

</style>
