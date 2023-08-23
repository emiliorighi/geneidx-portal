<template>
  <div class="page-wrapper">
    <div class="row justify-space-between align-end">
      <div class="flex">
        <h1 class="va-h1">geneid</h1>
        <p>Predict genic elements as splice sites, exons or genes, along eukaryotic DNA sequences</p>
      </div>
      <div class="flex">
        <va-button color="secondary" icon="ion-logo-github">
          Software and docs
        </va-button>
      </div>
    </div>
    <va-divider />
    <div class="row">
      <va-form @submit.prevent="submit" class="flex flex-col gap-6" tag="form" ref="geneid">
        <h2 class="va-h2">
          Input data
        </h2>
        <va-file-upload type="single" v-model="geneidPayload.fastaInput" dropzone
          drop-zone-text="Upload a fasta file to process" file-types=".fa,.fasta" />
        <va-file-upload type="single" v-model="geneidPayload.gffInput" dropzone drop-zone-text="Upload your GFF evidences"
          file-types=".gff,.gff3" />
        <h2 class="va-h2">
          Prediction options
        </h2>
        <suspense>
          <parameter-selection @param-selection="(value) => geneidPayload.paramFile = value" />
        </suspense>
        <va-radio class="mb-6" v-model="geneidPayload.mode" :error="isAssemblingMode && !Boolean(geneidPayload.gffInput)"
          :error-messages="[assemblingModeError]" :messages="[assemblingModeMessage]" :options="mode" value-by="value" />
        <va-radio class="mb-6" v-model="geneidPayload.strand" :messages="['Leave empty for both strands']" :options="strands" value-by="value" />
        <h2 class="va-h2">
          Ouput options
        </h2>
        <va-radio class="mb-6" v-model="geneidPayload.output" :options="output" text-by="text"
          :messages="['Leave empty for the default geneid output format']"></va-radio>
        <div class="row justify-start gap-6">
          <div class="flex">
            <div class="col">
              <span class="va-title mb-6">
                signals
              </span>
              <va-checkbox :disabled="isAssemblingMode" class="mb-6" v-for="(s, i) in signals" :array-value="s.value"
                :label="s.text" :key="i" v-model="geneidPayload.options"></va-checkbox>
            </div>
          </div>
          <div class="flex">
            <div class="col">
              <span class="va-title mb-6">
                exons
              </span>
              <va-checkbox :disabled="isAssemblingMode" v-for="(e, i) in exons" class="mb-6" :array-value="e.value"
                :label="e.text" :key="i" v-model="geneidPayload.options"></va-checkbox>
            </div>
          </div>
        </div>
        <va-card-actions align="between">
          <va-button color="danger" type="reset" @click="reset">Reset</va-button>
          <va-button type="submit">Submit</va-button>
        </va-card-actions>
      </va-form>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, reactive } from 'vue'
import { GeneidForm } from '../../data/types'
import { mode, strands, output, signals, exons } from '../../data/geneidParams'
import ParameterSelection from './ParameterSelection.vue'
import { useForm } from 'vuestic-ui'
import GeneidService from '../../services/clients/GeneidService'

const { isValid, validate, resetValidation } = useForm('geneid')

const initGeneidPayload: GeneidForm = {
  fastaInput: undefined,
  gffInput: undefined,
  mode: mode[0].value,
  strand: '',
  output: '',
  options: [],
  paramFile: ''
}
const geneidPayload = reactive({...initGeneidPayload})

const isFastaUploaded = computed(() => {
  return Boolean(geneidPayload.fastaInput)
})

const isAssemblingMode = computed(() => {
  const mode = geneidPayload.mode === '-O'
  if (mode) geneidPayload.options = []
  return mode
})


function reset(){
  Object.assign(geneidPayload, initGeneidPayload)
}

async function submit(){
  const formData = new FormData()
  Object.keys(geneidPayload).forEach( k => {
    const v = geneidPayload[k as keyof GeneidForm]
    if(v) formData.append(k, v)
  })
  console.log(formData)
  const {data} = await GeneidService.sendForm(formData)
  console.log(data)
  return data
}


function loadDemo(){

}
const assemblingModeError = 'Must insert GFF evidences with assembling mode.'
const assemblingModeMessage = 'Assembling mode is incompatible with Signals and Exons options'

</script>
<style scoped>
.col {
  display: flex;
  flex-direction: column;
}

.gap-6 {
  gap: 0.6rem;
}

.mb-6 {
  margin-bottom: 0.6rem;
}
</style>