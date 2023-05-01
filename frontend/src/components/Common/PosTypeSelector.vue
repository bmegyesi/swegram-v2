<template>
  <div class="selector-container">
    <div class="pos-selector-container sub-container">
      <span>Tag Set:</span>
      <el-radio-group
        v-model="tagset"
      >
        <el-radio
          label="upos"
        >
          UPOS
        </el-radio>
        <el-radio
          label="xpos"
        >
          XPOS
        </el-radio>
      </el-radio-group>
    </div>
    <div class="type-selector-container sub-container">
      <span>Type:</span>
      <el-radio-group
        v-model="typeset"
      >
        <el-radio
          label="form"
        >
          FORM
        </el-radio>
        <el-radio
          label="norm"
        >
          NORM
        </el-radio>
        <el-radio
          label="lemma"
        >
          LEMMA
        </el-radio>
      </el-radio-group>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tagset: 'upos',
      typeset: 'form',
    };
  },

  watch: {
    tagset(newValue) {
      this.$emit('tagSetChange', { newTagset: newValue });
    },
    typeset(newValue) {
      this.$emit('typeSetChange', { newTypeset: newValue });
    },
  },
};
</script>

<style scoped>

.selector-container {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
}

.sub-container {
  margin-bottom: 2em;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
}

.sub-container span {
  color: #606266;
  margin-right: 10px;
  font-size: 14px;
}

.sub-container .el-radio {
  margin-right: 10px;
}
</style>
