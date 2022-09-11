<template>
  <div>
    {{ content.slice(0, end).split(' ').slice(0,).join(' ') }}
    <el-button
      v-if="end < content.length - 1"
      type="text"
      @click="showmore()"
    >
      ...
    </el-button>
  </div>
</template>

<script>

export default {
  props: {
    content: {
      type: String,
      default: '',
      required: false,
    },
    level: {
      type: String,
      default: '',
      required: false,
    },
  },
  data() {
    return {
      length: 0,
      end: 0,
      step: 0,
    };
  },
  watch: {
    content(newValue) {
      this.length = newValue.length;
    },
  },
  mounted() {
    if (this.$props.level === 'sent') {
      this.end = 200;
      this.step = 200;
    } else if (this.$props.level === 'para') {
      this.end = 500;
      this.step = 500;
    } else if (this.$props.level === 'text') {
      this.end = 2000;
      this.step = 2000;
    }
  },
  methods: {
    showmore() {
      this.end += this.step;
    },
  },
};

</script>
