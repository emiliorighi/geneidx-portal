<template>
    <va-select :options="paramFiles" v-model="selectedParam" searchable text-by="species" value-by="parameter_file"
        label="selected a parameter file" stick-to-edges
        @update:modelValue="(value) => $emit('paramSelection', value)"></va-select>
</template>
<script setup lang="ts">
import * as d3 from 'd3'
import { ref } from 'vue'
const selectedParam = ref('')

const paramFilesMatrix = 'https://raw.githubusercontent.com/guigolab/geneid-parameter-files/main/matrix.tsv'

const paramFiles = await d3.tsv(paramFilesMatrix)

const emits = defineEmits(['paramSelection'])


</script>