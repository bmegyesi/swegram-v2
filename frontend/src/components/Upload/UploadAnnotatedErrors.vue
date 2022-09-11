<template>
  <el-main>
    <el-alert
      title="Detected annotated errors"
      type="warning"
      show-icon
      :closable="true"
      class="alertContainer"
      @close="resetErrors"
    >
      <el-row
        v-for="(error, index) in errors"
        :key="index"
      >
        <el-alert
          :title="'Error Type: ' + error.error_type"
          type="error"
          :closable="true"
          class="errorItem"
          @close="removeErrorNumber"
        >
          <p>{{ error.error_prompt }}</p>
          <p>{{ error.content }}</p>
        </el-alert>
      </el-row>
    </el-alert>
  </el-main>
</template>

<script>

export default {
  props: {
    errors: {
      type: Array,
      default: () => [],
      require: false,
    },
  },
  data() {
    return {
      errorLength: 0,
    };
  },
  watch: {
    errorLength() {
      if (this.errorLength === 0) {
        this.$emit('clearErrors');
      }
    },
  },
  mounted() {
    this.errorLength = this.$props.errors.length;
  },
  methods: {
    resetErrors() {
      this.$emit('clearErrors');
    },
    removeErrorNumber() {
      this.errorLength -= 1;
    },
  },
};
</script>

<style scoped>
  .errorItem {
    width: 75vw;
    text-align: left;
  }
</style>
