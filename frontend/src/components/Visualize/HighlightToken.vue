<script setup>
import { ref, watch, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue'

const props = defineProps({
    tokens: {
        type: Array,
        default: () => [],
        required: false,
    },
});

const emit = defineEmits(['searchQuery']);

const input = ref('');
const select = ref(null);
const forms = ref([]);
const norms = ref([]);
const lemmas = ref([]);
const uposes = ref([]);
const xposes = ref([]);
const feats = ref([]);
const ufeats = ref([]);
const deprels = ref([]);

watch(select, () => {
    input.value = '';
});

watch(
    () => props.tokens,
    () => {
        initialize();
        if (input.value && select.value) {
            emit('searchQuery', { query: input.value, type: select.value });
        }
    },
);

onMounted(() => initialize());

function handleQuerySearch(query) {
    emit('searchQuery', { query, type: select.value });
}

function querySearch(queryStr, cb) {
    let re = [];
    const queryString = queryStr || '';

    if (select.value === 'form') {
        re = forms.value.filter((token) => token.startsWith(queryString));
    } else if (select.value === 'norm') {
        re = norms.value.filter((token) => token.startsWith(queryString));
    } else if (select.value === 'lemma') {
        re = lemmas.value.filter((token) => token.startsWith(queryString));
    } else if (select.value === 'upos') {
        re = uposes.value.filter((pos) => pos.startsWith(queryString));
    } else if (select.value === 'xpos') {
        re = xposes.value.filter((pos) => pos.startsWith(queryString));
    } else if (select.value === 'deprel') {
        re = deprels.value.filter((rel) => rel.startsWith(queryString));
    } else if (select.value === 'feats') {
        re = feats.value.filter((feat) => feat.startsWith(queryString));
    } else if (select.value === 'ufeats') {
        re = ufeats.value.filter((ufeat) => ufeat.startsWith(queryString));
    }

    if (select.value) {
        cb(re.map((t) => ({ value: t })));
    } else {
        cb([{ value: 'Query is not set!' }]);
    }
}

function initializeType(type) {
    if (type === 'feats') {
        const set = new Set();
        props.tokens.forEach((token) => {
            (token.feats || '').split(/[|/]/).forEach((feat) => {
                set.add(feat);
            });
        });
        set.delete('-');
        set.delete('_');
        return [...set];
    }
    if (type === 'ufeats') {
        const set = new Set();
        props.tokens.forEach((token) => {
            (token.ufeats || '').split(/[|=]/).forEach((feat) => {
                set.add(feat);
            });
        });
        set.delete('-');
        set.delete('_');
        return [...set];
    }
    return [...new Set(props.tokens.map((token) => token[type]))];
}

function initialize() {
    forms.value = initializeType('form');
    norms.value = initializeType('norm');
    lemmas.value = initializeType('lemma');
    uposes.value = initializeType('upos');
    xposes.value = initializeType('xpos');
    feats.value = initializeType('feats');
    ufeats.value = initializeType('ufeats');
    deprels.value = initializeType('deprel');
}
</script>

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
      <template #suffix>
        <el-icon class="el-input__icon">
          <Search />
        </el-icon>
      </template>
      <template #prepend>
        <el-select
          v-model="select"
          placeholder="Query"
        >
          <el-option label="form" value="form" />
          <el-option label="norm" value="norm" />
          <el-option label="lemma" value="lemma" />
          <el-option label="upos" value="upos" />
          <el-option label="xpos" value="xpos" />
          <el-option label="deprel" value="deprel" />
          <el-option label="feats" value="feats" />
          <el-option label="ufeats" value="ufeats"/>
        </el-select>
      </template>
    </el-autocomplete>
  </el-col>
</template>

<style scoped>

.el-select {
  width: 90px;
}

</style>
