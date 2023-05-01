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
      <template slot-scope="scope">
        <el-button
          type="text"
          size="small"
          icon="el-icon-delete"
          @click="handleTokenDeleteClick(scope.row.index, scope.row.frequency, scope.row.pos)"
        />
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
    category: {
      type: String,
      default: '',
      require: true,
    },
    tagset: {
      type: String,
      default: '',
      require: true,
    },
  },
  methods: {
    handleTokenDeleteClick(i, f, p) {
      this.$emit('deleteToken', ({ i, f, p }));
    },
  },
};
</script>

<style scoped>

.el-button {
  margin: 0 10px 0 10px;
}

</style>
