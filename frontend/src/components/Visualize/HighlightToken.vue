<template>
  <el-col
    :span="12"
    class="demo-autocomplete"
  >
    <el-autocomplete
      v-model="input"
      class="input-with-select"
      :fetch-suggestions="querySearch"
      placeholder="Search"
      @input="handleQuerySearch"
    >
      <i
        slot="suffix"
        class="el-icon-search el-input__icon"
      />
      <el-select
        slot="prepend"
        v-model="select"
        placeholder="Query"
      >
        <el-option
          label="form"
          value="form"
        />
        <el-option
          label="norm"
          value="norm"
        />
        <el-option
          label="lemma"
          value="lemma"
        />
        <el-option
          label="upos"
          value="upos"
        />
        <el-option
          label="xpos"
          value="xpos"
        />
        <el-option
          label="deprel"
          value="deprel"
        />
        <el-option
          label="feats"
          value="feats"
        />
        <el-option
          label="ufeats"
          value="ufeats"
        />
      </el-select>
    </el-autocomplete>
  </el-col>
</template>

<script>

export default {
  props: {
    tokens: {
      type: Array,
      default: () => [],
      required: false,
    },
  },
  data() {
    return {
      input: '',
      select: null,
      forms: '',
      norms: '',
      lemmas: '',
      uposes: '',
      xposes: '',
      feats: '',
      ufeats: '',
      deprels: '',
    };
  },
  watch: {
    select() {
      // re-select search type and clear the input
      this.input = '';
    },
    tokens() {
      this.initialize();
      if (this.input && this.select) {
        this.$emit('searchQuery', { query: this.input, type: this.select });
      }
    },
  },
  mounted() {
    this.initialize();
  },
  methods: {
    handleQuerySearch(query) {
      this.$emit('searchQuery', { query, type: this.select });
    },
    querySearch(queryStr, cb) {
      let re;
      // this function will be triggered when focusing;
      const queryString = queryStr || '';

      if (this.select === 'form') {
        re = this.forms.filter((token) => token.startsWith(queryString));
      } else if (this.select === 'norm') {
        re = this.norms.filter((token) => token.startsWith(queryString));
      } else if (this.select === 'lemma') {
        re = this.lemmas.filter((token) => token.startsWith(queryString));
      } else if (this.select === 'upos') {
        re = this.uposes.filter((pos) => pos.startsWith(queryString));
      } else if (this.select === 'xpos') {
        re = this.xposes.filter((pos) => pos.startsWith(queryString));
      } else if (this.select === 'deprel') {
        re = this.deprels.filter((rel) => rel.startsWith(queryString));
      } else if (this.select === 'feats') {
        re = this.feats.filter((feat) => feat.startsWith(queryString));
      } else if (this.select === 'ufeats') {
        re = this.ufeats.filter((ufeat) => ufeat.startsWith(queryString));
      }
      // callback functions
      if (this.select) {
        cb(re.map((t) => ({ value: t })));
      } else {
        cb([{ value: 'Query is not set!' }]);
      }
      // need to update style of tokens in the parental component
      // we send the queryString and query type
    },
    initializeType(type) {
      if (type === 'feats') {
        const feats = new Set();
        this.$props.tokens.forEach((token) => {
          token.feats.split(/[|/]/).forEach((feat) => {
            feats.add(feat);
          });
        });
        feats.delete('-');
        feats.delete('_');
        return [...feats];
      } if (type === 'ufeats') {
        const ufeats = new Set();
        this.$props.tokens.forEach((token) => {
          token.ufeats.split(/[|=]/).forEach((feat) => {
            ufeats.add(feat);
          });
        });
        ufeats.delete('-');
        ufeats.delete('_');
        return [...ufeats];
      }
      return [...new Set(this.$props.tokens.map((token) => token[type]))];
    },
    initialize() {
      this.forms = this.initializeType('form');
      this.norms = this.initializeType('norm');
      this.lemmas = this.initializeType('lemma');
      this.uposes = this.initializeType('upos');
      this.xposes = this.initializeType('xpos');
      this.feats = this.initializeType('feats');
      this.ufeats = this.initializeType('ufeats');
      this.deprels = this.initializeType('deprel');
    },
  },
};
</script>

<style scoped>

.el-select {
  width: 90px;
}

</style>
