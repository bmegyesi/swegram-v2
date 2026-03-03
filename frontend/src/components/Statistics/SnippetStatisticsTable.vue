<script setup>
const props = defineProps({
    statisticsTableData: {
        type: Object,
        default: null,
    },
    loadingOverview: {
        type: Boolean,
        default: false,
    },
    level: {
        type: String,
        default: 'text',
    },
})

function getRowId(row) {
    return row.name
}

function getFeatureName(feature) {
    if (feature) {
      const fn = feature
          .replace('(', '')
          .replace(')', '')
          .replace(' & ', ' ')
          .replace('-', ' ')
          .split(' ')
      const head = fn.slice(0, 1).join().toLowerCase()
      const tail = fn.slice(1).map((w) => w[0].toUpperCase() + w.slice(1).toLowerCase())
      return head + tail.join('')
    }
    return feature
}
</script>

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
          v-for="statAspect in props.statisticsTableData.data"
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
              <template #default="{ row }">
                <span>
                  <el-tooltip
                    v-if="row && row.name"
                    class="item"
                    effect="dark"
                    :content="$t(`featuresDef.${getFeatureName(row.name)}`)"
                    placement="right"
                  >
                    <span>{{ $t(`features.${getFeatureName(row.name)}`) }}</span>
                  </el-tooltip>
                  <span v-else>-</span>
                </span>
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
