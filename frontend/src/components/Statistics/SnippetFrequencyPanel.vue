<template>
  <div
    class="frequency-container"
  >
    <el-popover
      placement="right"
      width="150"
      trigger="click"
    >
      <el-table
        :data="data"
        height="300px"
      >
        <el-table-column
          width="80"
          property="pos"
          :label="tagset.toUpperCase()"
        />
        <el-table-column
          prop="model"
          label="Toggle"
          width="70"
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
      <el-button
        slot="reference"
      >
        Select PoS
      </el-button>
    </el-popover>
    <el-radio-group
      v-model="frequencyType"
      size="small"
    >
      <el-radio
        label="showType"
        border
        @change="getTypePoS"
      >
        Show frequency statistics for type
      </el-radio>
      <el-radio
        label="showPoS"
        border
        @change="getTypePoS"
      >
        Show frequency statistics for PoS
      </el-radio>
    </el-radio-group>
  </div>
</template>

<script>
export default {
  props: {
    dataList: {
      type: Array,
      default: () => [],
      require: false,
    },
    category: {
      type: String,
      default: () => '',
      require: false,
    },
    tagset: {
      type: String,
      default: () => '',
      require: false,
    },
  },
  data() {
    return {
      frequencyType: 'showType',
      data: [],
    };
  },
  watch: {
    dataList(newValue) {
      const notDisplayAll = newValue.map((entry) => entry.model).includes(false);
      this.data = [{ pos: 'ALL', model: !notDisplayAll, frequency: null }, ...newValue];
    },
  },
  mounted() {
    this.data = [{ pos: 'ALL', model: true, frequency: null }, ...this.$props.dataList];
  },
  methods: {
    handlePoSSwitch(state, pos, f) {
      this.$emit('switchPos', ({ state, pos, f }));
    },
    getTypePoS(value) {
      this.$emit('changeShowType', (value));
    },
  },
};
</script>

<style scoped>
.frequency-container {
  display: flex;
}

.el-radio-group {
  display: flex;
  margin: 10px;
}

.el-button {
  margin: 0 10px 0 10px;
}

</style>
