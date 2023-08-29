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
          drop-zone-text="Upload a fasta file to process" file-types=".fa,.fasta,.fna" />
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
        <va-radio class="mb-6" v-model="geneidPayload.strand" :messages="['Leave empty for both strands']"
          :options="strands" value-by="value" />
        <h2 class="va-h2">
          Ouput options
        </h2>
        <va-radio class="mb-6" v-model="geneidPayload.output" :options="output" text-by="text" value-by="value"
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
    <div ref="transcript">
      <TranscriptViewer />
    </div>
    <div>
      <Jbrowse2 v-if="showJBrowse" :assembly="jbrowse.assembly" :tracks="jbrowse.tracks" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { AssemblyAdapter, GeneidForm } from '../../data/types'
import { mode, strands, output, signals, exons } from '../../data/geneidParams'
import ParameterSelection from './ParameterSelection.vue'
import { useForm } from 'vuestic-ui'
import GeneidService from '../../services/clients/GeneidService'
import TranscriptViewer from '../../components/viz/TranscriptViewer.vue'
import * as d3 from 'd3'
import Jbrowse2 from '../../components/genome-browser/Jbrowse2.vue'
const jbrowse = reactive({
  assembly: {},
  tracks: []
})
onMounted(() => {
  const { assembly, annotations } = createJBrowseData()

  jbrowse.assembly = { ...assembly }
  jbrowse.tracks = [...annotations]
  // tracks.value = [...annotations]
  showJBrowse.value = true
})

const chromosomes = [
  {
    "_id": {
      "$oid": "6309484e23649397d129f97d"
    },
    "accession_version": "LR584231.2",
    "metadata": {
      "name": "1",
      "length": "29232231",
      "gc_count": "12957850"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f989"
    },
    "accession_version": "LR584232.1",
    "metadata": {
      "name": "13",
      "length": "21507415",
      "gc_count": "9617372"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f991"
    },
    "accession_version": "LR584233.2",
    "metadata": {
      "name": "21",
      "length": "20050447",
      "gc_count": "8710680"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f984"
    },
    "accession_version": "LR584234.2",
    "metadata": {
      "name": "8",
      "length": "19721368",
      "gc_count": "8939241"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f98f"
    },
    "accession_version": "LR584235.1",
    "metadata": {
      "name": "19",
      "length": "19418397",
      "gc_count": "8625870"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f990"
    },
    "accession_version": "LR584236.2",
    "metadata": {
      "name": "20",
      "length": "18239318",
      "gc_count": "8218569"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f97f"
    },
    "accession_version": "LR584237.1",
    "metadata": {
      "name": "3",
      "length": "17484280",
      "gc_count": "7881115"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f983"
    },
    "accession_version": "LR584238.1",
    "metadata": {
      "name": "7",
      "length": "17515293",
      "gc_count": "7989326"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f98d"
    },
    "accession_version": "LR584239.2",
    "metadata": {
      "name": "17",
      "length": "16842301",
      "gc_count": "7681465"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f98b"
    },
    "accession_version": "LR584240.2",
    "metadata": {
      "name": "15",
      "length": "16705553",
      "gc_count": "7593546"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f987"
    },
    "accession_version": "LR584241.1",
    "metadata": {
      "name": "11",
      "length": "16367601",
      "gc_count": "7459706"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f980"
    },
    "accession_version": "LR584242.2",
    "metadata": {
      "name": "4",
      "length": "16363587",
      "gc_count": "7321731"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f992"
    },
    "accession_version": "LR584243.1",
    "metadata": {
      "name": "22",
      "length": "16056980",
      "gc_count": "7302820"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f98a"
    },
    "accession_version": "LR584244.1",
    "metadata": {
      "name": "14",
      "length": "16036328",
      "gc_count": "7171193"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f97e"
    },
    "accession_version": "LR584245.2",
    "metadata": {
      "name": "2",
      "length": "15686389",
      "gc_count": "7216912"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f985"
    },
    "accession_version": "LR584246.2",
    "metadata": {
      "name": "9",
      "length": "15473624",
      "gc_count": "6971049"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f981"
    },
    "accession_version": "LR584247.1",
    "metadata": {
      "name": "5",
      "length": "14586308",
      "gc_count": "6627873"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f988"
    },
    "accession_version": "LR584248.2",
    "metadata": {
      "name": "12",
      "length": "13571579",
      "gc_count": "6257139"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f98c"
    },
    "accession_version": "LR584249.2",
    "metadata": {
      "name": "16",
      "length": "13527504",
      "gc_count": "6209930"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f982"
    },
    "accession_version": "LR584250.1",
    "metadata": {
      "name": "6",
      "length": "12913240",
      "gc_count": "5896118"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f986"
    },
    "accession_version": "LR584251.2",
    "metadata": {
      "name": "10",
      "length": "12556898",
      "gc_count": "5742224"
    }
  },
  {
    "_id": {
      "$oid": "6309484e23649397d129f98e"
    },
    "accession_version": "LR584252.2",
    "metadata": {
      "name": "18",
      "length": "10237708",
      "gc_count": "4852600"
    }
  }
]

const showJBrowse = ref(false)
const { isValid, validate, resetValidation } = useForm('geneid')
const transcript = ref()
const initGeneidPayload: GeneidForm = {
  fastaInput: undefined,
  gffInput: undefined,
  mode: mode[0].value,
  strand: '',
  output: '',
  options: [],
  paramFile: ''
}
const geneidPayload = reactive({ ...initGeneidPayload })
const isFastaUploaded = computed(() => {
  return Boolean(geneidPayload.fastaInput)
})
const isAssemblingMode = computed(() => {
  const mode = geneidPayload.mode === '-O'
  if (mode) geneidPayload.options = []
  return mode
})

function reset() {
  Object.assign(geneidPayload, initGeneidPayload)
}

async function submit() {
  const formData = new FormData()
  Object.keys(geneidPayload).forEach(k => {
    const v = geneidPayload[k as keyof GeneidForm]
    if (v) formData.append(k, v)
  })
  const { data } = await GeneidService.sendForm(formData)
  console.log(d3.tsvParse(data))
  return data
}

function createJBrowseData() {
  const assembly: AssemblyAdapter = {
    name: 'fTakRub1.2',
    sequence: {
      name: 'fTakRub1.2',
      trackId: 'GCA_901000725.2',
      type: 'ReferenceSequenceTrack',
      adapter: {
        type: 'RefGetAdapter',
        sequenceData:
          chromosomes.reduce((previousObject, currentObject) => {
            const key = `insdc:${currentObject.accession_version}`
            return Object.assign(previousObject, {
              [key]: {
                name: currentObject.metadata.name,
                size: Number(currentObject.metadata.length)
              }
            })
          }, {})
      }
    }
  }
  const annotations = [
    {
      type: "FeatureTrack",
      trackId: 'fTakRub1.2_ensembl',
      name: 'fTakRub1.2_ensembl',
      assemblyNames: ['fTakRub1.2'],
      category: ["Genes"],
      adapter: {
        type: "Gff3TabixAdapter",
        gffGzLocation: {
          uri: 'http://localhost:99/api/geneid/genes.sorted.gff3.gz',
          locationType: "UriLocation"
        },
        index: {
          location: {
            uri: 'http://localhost:99/api/geneid/genes.sorted.gff3.gz.tbi',
            locationType: "UriLocation"
          }
        }
      }
    }
  ]
  return { assembly, annotations }
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