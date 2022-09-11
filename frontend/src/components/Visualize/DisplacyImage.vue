<template>
  <el-image
    :src="url"
    :preview-src-list="srcList"
  />
</template>

<script>
import displaCy from '../../../lib/displacy';

export default {
  // props: ['sentence'],
  props: {
    sentence: {
      type: Object,
      default: null,
      required: false,
    },
  },
  data() {
    return {
      url: '',
    };
  },
  computed: {
    srcList() {
      return [this.url];
    },
  },
  watch: {
    sentence(newValue) {
      this.renderSentenceFeatures(newValue);
    },
  },
  mounted() {
    this.renderSentenceFeatures(this.$props.sentence);
  },
  methods: {
    renderSentenceFeatures(sentence) {
      // if (this.src) {
      //   return;
      // }
      // eslint-disable-next-line new-cap
      const d = new displaCy('', {});
      const parse = this.displacyJSONFromSentenceData(sentence);
      const result = d.render(parse);
      this.url = result;
    },
    displacyJSONFromSentenceData(sentence) {
      const words = sentence.tokens.map((originalWord) => ({
        tag: originalWord.upos,
        text: originalWord.form,
      }));
      words.unshift({ tag: 'ROOT', text: 'ROOT' });
      const arcs = [];
      sentence.tokens
        .filter(
          (originalWord) => originalWord.head !== 0, // 0 or '0'
        )
        .forEach((originalWord) => {
          // Minus 1 to fix word index from 1 instead of 0
          // const tokenId = parseInt(originalWord.token_id, 10) - 1;
          // const head = parseInt(originalWord.head, 10) - 1;
          const tokenId = parseInt(originalWord.token_id, 10);
          const head = parseInt(originalWord.head, 10);
          const arc = {
            // spaCy's JSON format requires start to be always smaller then end
            start: head < tokenId ? head : tokenId,
            end: head < tokenId ? tokenId : head,
            label: originalWord.deprel,
            dir: head < tokenId ? 'left' : 'right',
          };
          arcs.push(arc);
        });
      return { arcs, words };
    },
  },
};
</script>
