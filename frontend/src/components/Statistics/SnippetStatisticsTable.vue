<template>
  <div>
    <!-- <el-divider content-position="left">
      Statistics
    </el-divider> -->
    <div
      v-loading="loadingOverview"
      class="statistics-container"
    >
      <el-collapse>
        <el-collapse-item
          v-for="statAspect in statisticsTableData.data"
          :key="statAspect.aspect"
          :title="$t(`features.${statAspect.aspect.toLowerCase()}`)"
        >
          <el-table
            :data="statAspect.data"
            :row-key="getRowId"
            stripe
          >
            <el-table-column
              prop="name"
              :label="$t('statistics.name')"
            >
              <template slot-scope="scope">
                <el-tooltip
                  class="item"
                  effect="dark"
                  :content="$t(`featuresDef.${getFeatureName(scope.row.name)}`)"
                  placement="right"
                >
                  <!-- <p>
                    <vue-mathjax :formula="formula"></vue-mathjax>
                  </p> -->
                  <span>{{ $t(`features.${getFeatureName(scope.row.name)}`) }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column
              prop="median"
              :label="
                level === 'sent' && statAspect.aspect !== 'general'
                  ? ''
                  : $t('statistics.median')"
            />
            <el-table-column
              prop="mean"
              :label="
                level === 'sent' && statAspect.aspect !== 'general'
                  ? ''
                  : $t('statistics.mean')"
            />
            <el-table-column
              prop="scalar"
              :label="$t('statistics.total')"
            />
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script>

export default {
  props: {
    statisticsTableData: {
      type: Object,
      default: null,
      required: false,
    },
    loadingOverview: {
      type: Boolean,
      default: false,
      required: false,
    },
    level: {
      type: String,
      default: '',
      required: false,
    },
  },
  methods: {
    getRowId(row) {
      return row.name;
    },
    getFeatureName(feature) {
      const fn = feature
        .replace('(', '')
        .replace(')', '')
        .replace(' & ', ' ')
        .replace('-', ' ')
        .split(' ');
      const head = fn.slice(0, 1).join().toLowerCase();
      const tail = fn.slice(1)
        .map((w) => w[0].toUpperCase() + w.slice(1).toLowerCase());
      return head + tail.join('');
    },
  },
};
</script>

<style scoped>

</style>
