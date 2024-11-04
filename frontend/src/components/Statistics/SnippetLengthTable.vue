<template>
  <el-table
    :data="dataList"
    border
    max-height="650px"
    :summary-method="getSummaries"
    show-summary
    fit
  >
    <el-table-column
      v-for="item in theadList"
      :key="item.label"
      :label="item.label"
      :prop="item.prop"
      :width="getColumnWidth(item.label)"
      :fixed="fixedColumnPosition(item.prop)"
    >
      <template
        slot="header"
        slot-scope="scope"
      >
        <el-row>
          {{ scope.column.label }}
        </el-row>
        <el-row>
          <el-button
            icon="el-icon-sort-down"
            size="mini"
            circle
            type="primary"
            @click="handleColumnSortDownClick(scope.column.label)"
          />
          <el-button
            icon="el-icon-sort-up"
            size="mini"
            circle
            type="sucess"
            @click="handleColumnSortUpClick(scope.column.label)"
          />
          <el-button
            v-if="scope.column.label !== 'Length' && scope.column.label !== 'Total'"
            icon="el-icon-close"
            size="mini"
            circle
            type="danger"
            @click="handleColumnDeleteClick(scope.column.label)"
          />
        </el-row>
      </template>
      <template slot-scope="scope">
        <el-container
          v-if="scope.row[item.prop].total === 0"
        >
          <el-button
            disabled
            size="mini"
          >
            -
          </el-button>
        </el-container>
        <el-container
          v-else-if="item.prop === 'Total'"
        >
          {{ scope.row[item.prop].total }}
        </el-container>
        <el-container
          v-else
        >
          <el-button
            v-if="item.prop === 'Length'"
            icon="el-icon-close"
            size="mini"
            type="danger"
            @click="handleRowDeleteClick(scope.row.Length.total)"
          />
          <el-popover
            trigger="click"
            placement="right"
          >
            <el-table
              :data="scope.row[item.prop].data"
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
            <el-button
              slot="reference"
              size="mini"
            >
              {{ scope.row[item.prop].total }}
            </el-button>
          </el-popover>
        </el-container>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>

export default {
  props: {
    dataList: {
      type: Array,
      default: () => [],
    },
    theadList: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    getColumnWidth(label){
      if (label == "Length" || label == "Total") {
        return 90;
      }
      return 130;
    },
    fixedColumnPosition(prop) {
      if (prop === 'Length') {
        return true;
      } if (prop === 'Total') {
        return 'right';
      }
      return false;
    },
    getSummaries(param) {
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
    },
    handleColumnDeleteClick(label) {
      this.$emit('deleteColumn', (label));
    },
    handleColumnSortDownClick(label) {
      this.$emit('sortUp', (label));
    },
    handleColumnSortUpClick(label) {
      this.$emit('sortDown', (label));
    },
    handleRowDeleteClick(row) {
      this.$emit('deleteRow', (row));
    },
  },
};
</script>

<style scoped>

.el-table th {
  /* to force the columns to be correctly aligned */
  display: table-cell!important;
}

</style>
