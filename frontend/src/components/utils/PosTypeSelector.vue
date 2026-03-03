<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['tagSetChange', 'typeSetChange'])

const tagset = ref('upos')
const typeset = ref('form')

watch(tagset, (newValue) => {
  emit('tagSetChange', { newTagset: newValue })
})

watch(typeset, (newValue) => {
  emit('typeSetChange', { newTypeset: newValue })
})
</script>

<template>
  <div class="selector-container">
    <div class="pos-selector-container sub-container">
      <span>Tag Set:</span>
      <el-radio-group
        v-model="tagset"
      >
        <el-radio
          value="upos"
        >
          UPOS
        </el-radio>
        <el-radio
          value="xpos"
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
          value="form"
        >
          FORM
        </el-radio>
        <el-radio
          value="norm"
        >
          NORM
        </el-radio>
        <el-radio
          value="lemma"
        >
          LEMMA
        </el-radio>
      </el-radio-group>
    </div>
  </div>
</template>

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
