<script setup>
  import { ref, watch } from 'vue'
import { Close, SortDown, SortUp } from '@element-plus/icons-vue'

const props = defineProps({
  dataList: {
    type: Array,
    default: () => [],
  },
  theadList: {
    type: Array,
    default: () => [],
  },
});

const tableData = ref([...props.dataList])
const theadData = ref([...props.theadList])

const emit = defineEmits(['deleteColumn', 'sortUp', 'sortDown', 'deleteRow']);

function getColumnWidth(label) {
  if (label === 'Length' || label === 'Total') {
    return 90;
  }
  return 130;
}

function fixedColumnPosition(prop) {
  if (prop === 'Length') {
    return true;
  }
  if (prop === 'Total') {
    return 'right';
  }
  return false;
}

function getSummaries(param) {
  const { columns, data } = param;
  const sums = [];
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = 'Total';
      return;
    }
    const values = data.map((item) => item[column.property].total);
    sums[index] = values.reduce((prev, curr) => prev + curr, 0);
  });
  return sums;
}

const handleColumnDeleteClick = (label) => {
  emit('deleteColumn', label);
};

const handleColumnSortDownClick = (label) => {
  emit('sortUp', label);
};

const handleColumnSortUpClick = (label) => {
  emit('sortDown', label);
};

const handleRowDeleteClick = (row) => {
  emit('deleteRow', row);
};

watch(
  () => props.dataList,
  (newVal) => {
    tableData.value = [...newVal] // update local reactive copy
  },
  { deep: true, immediate: true }
)

watch(
  () => props.theadList,
  (newVal) => {
    theadData.value = [...newVal] // update local reactive copy
  },
  { deep: true, immediate: true }
)

</script>

<template>
  <el-table
    :data="tableData"
    border
    max-height="650px"
    :summary-method="getSummaries"
    show-summary
    fit
  >
    <el-table-column
      v-for="item in theadData"
      :key="item.label"
      :label="item.label"
      :prop="item.prop"
      :width="getColumnWidth(item.label)"
      :fixed="fixedColumnPosition(item.prop)"
    >
      <template
        #header="{ column }"
      >
        <el-row>
          {{ column.label }}
        </el-row>
        <el-row>
          <el-button
            text
            type="primary"
            class="icon-btn-xs"
            @click.stop="handleColumnSortDownClick(column.label)"
          >
            <el-icon :size="12">
              <SortDown />
            </el-icon>
          </el-button>
          <el-button
            text
            class="icon-btn-xs"
            @click.stop="handleColumnSortUpClick(column.label)"
          >
            <el-icon :size="12">
              <SortUp />
            </el-icon>
          </el-button>
          <el-button
            v-if="column.label !== 'Length' && column.label !== 'Total'"
            text
            type="danger"
            class="icon-btn-xs"
            @click.stop="handleColumnDeleteClick(column.label)"
          >
            <el-icon :size="12">
              <Close />
            </el-icon>
          </el-button>
        </el-row>
      </template>
      <template #default="{ row }">
        <el-container
          v-if="row[item.prop].total === 0"
        >
          <el-button
            disabled
            size="small"
          >
            -
          </el-button>
        </el-container>
        <el-container
          v-else-if="item.prop === 'Total'"
        >
          {{ row[item.prop].total }}
        </el-container>
        <el-container
          v-else
        >
          <el-button
            v-if="item.prop === 'Length'"
            text
            type="danger"
            class="icon-btn-xs"
            @click.stop="handleRowDeleteClick(row.Length.total)"
          >
            <el-icon :size="14">
              <Close />
            </el-icon>
          </el-button>
          <el-popover
            trigger="click"
            placement="right"
          >
            <el-table
              :data="row[item.prop].data"
              max-height="300px"
            >
              <el-table-column
                prop="type"
                label="type"
              />
              <el-table-column
                prop="count"
                label="count"
              />
            </el-table>
            <template #reference>
              <el-button
                size="small"
              >
                {{ row[item.prop].total }}
              </el-button>
            </template>
          </el-popover>
        </el-container>
      </template>
    </el-table-column>
  </el-table>
</template>

<style scoped>

.el-table th {
  /* to force the columns to be correctly aligned */
  display: table-cell!important;
}

.icon-btn-xs {
  padding: 0 !important;
  min-width: 16px !important;
  height: 16px !important;
  border-radius: 3px;
}

</style>
