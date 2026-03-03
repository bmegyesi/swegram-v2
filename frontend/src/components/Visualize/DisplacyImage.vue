<script setup>
import { ref, computed, watch } from 'vue';
import displaCy from '@/components/lib/displacy';

const props = defineProps({
  sentence: {
    type: Object,
    default: null,
  },
});

const url = ref('');
const srcList = computed(() => [url.value]);

function displacyJSONFromSentenceData(sentence) {
  if (!sentence || !sentence.tokens) return { arcs: [], words: [] };

  const words = sentence.tokens.map((originalWord) => ({
    tag: originalWord.upos,
    text: originalWord.form,
  }));
  words.unshift({ tag: 'ROOT', text: 'ROOT' });

  const arcs = [];
  sentence.tokens
    .filter((originalWord) => originalWord.head !== 0)
    .forEach((originalWord) => {
      const tokenId = parseInt(originalWord.token_id, 10);
      const head = parseInt(originalWord.head, 10);
      const arc = {
        start: head < tokenId ? head : tokenId,
        end: head < tokenId ? tokenId : head,
        label: originalWord.deprel,
        dir: head < tokenId ? 'left' : 'right',
      };
      arcs.push(arc);
    });

  return { arcs, words };
}

function renderSentenceFeatures(sentence) {
  const d = new displaCy('', {});
  const parse = displacyJSONFromSentenceData(sentence);
  const result = d.render(parse);
  url.value = result;
}

watch(() => props.sentence, (newValue) => {
  renderSentenceFeatures(newValue);
}, { immediate: true });
</script>

<template>
  <el-image
    :src="url"
    :preview-src-list="srcList"
  />
</template>
