
<script setup>
import { toRefs } from 'vue'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps({
    dataList: {
        type: Array,
        default: () => [],
    },
    category: {
        type: String,
        default: '',
        required: true,
    },
    tagset: {
        type: String,
        default: '',
        required: true,
    },
})

const { dataList, category, tagset } = toRefs(props)

const emit = defineEmits(['deleteToken'])

function handleTokenDeleteClick(i, f, p) {
    emit('deleteToken', { i, f, p })
}
</script>

<template>
  <el-table
    :data="dataList"
    height="450"
    style="width: 90%"
    striped
  >
    <el-table-column
      prop="index"
      label="Rank"
      width="100"
      sortable
    />
    <el-table-column
      prop="token"
      :label="category.toUpperCase()"
      width="160"
      sortable
    />
    <el-table-column
      prop="pos"
      :label="tagset.toUpperCase()"
      width="120"
      sortable
    />
    <el-table-column
      prop="frequency"
      label="Frequency"
      width="120"
    />
    <el-table-column
      prop="ratio"
      label="Ratio"
      width="120"
    />
    <el-table-column
      label="Delete"
      width="140"
    >
      <template #default="scope">
        <el-button
          link
          size="small"
          :icon="Delete"
          @click="handleTokenDeleteClick(scope.row.index, scope.row.frequency, scope.row.pos)"
        />
      </template>
    </el-table-column>
  </el-table>
</template>

<style scoped>

.el-button {
  margin: 0 10px 0 10px;
}

</style>
