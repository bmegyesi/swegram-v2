<template>
  <el-table
    :data="dataList"
    height="450"
    style="width: 90%"
    :default-sort="{prop:'index', order: 'desceding'}"
    striped
  >
    <el-table-column
      prop="index"
      label="Rank"
      sortable
      width="100"
    />
    <el-table-column
      prop="pos"
      :label="tagset.toUpperCase()"
      sortable
      width="120"
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
      prop="model"
      label="Toggle"
      width="140"
    >
      <template slot-scope="scope">
        <el-switch
          v-model="scope.row.model"
          active-color="#409EFF"
          inactive-color="#C0C4CC"
          @change="handlePoSSwitch(scope.row.model, scope.row.pos, scope.row.frequency)"
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
      required: false,
    },
    tagset: {
      type: String,
      default: '',
      required: true,
    },
  },
  methods: {
    handlePoSSwitch(state, pos, f) {
      // s p f: boolean, pos, frequency
      this.$emit('switchPoS', ({ state, pos, f }));
    },
  },
};
</script>
