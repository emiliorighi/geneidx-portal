<template>
  <div style="padding:20px">
    <div class="row justify-start">
      <div class="flex"><va-button size="small" @click="downloadSVGImage(tree)">SVG</va-button></div>
      <div class="flex"><va-button size="small" @click="downloadPGNImage(tree)">PNG</va-button></div>
    </div>
    <svg ref="tree" style="width: 1000px"></svg>
  </div>
</template>
<script lang="ts" setup>
import * as d3 from 'd3'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTreeData } from './setTreeData'
import { createIndentedTree } from './scripts/createIndentedTree'
import { downloadSVGImage, downloadPGNImage } from './scripts/generateImage'

const router = useRouter()
const tree = ref(null)

const props = defineProps<{
  data: Object
}>()

const { root } = useTreeData(props.data)

onMounted(() => {
  createIndentedTree(tree, root)
})
</script>
