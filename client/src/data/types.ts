import type { TChartData as ChartData } from 'vue-chartjs/dist/types'

export type ColorThemes = {
  [key: string]: string
}

export type TLineChartData = ChartData<'line'>
export type TBarChartData = ChartData<'bar'>
export type TBubbleChartData = ChartData<'bubble'>
export type TDoughnutChartData = ChartData<'doughnut'>
export type TPieChartData = ChartData<'pie'>

export type TChartData = TLineChartData | TBarChartData | TBubbleChartData | TDoughnutChartData | TPieChartData

export interface GeneidForm {
  fastaInput: File | undefined,
  gffInput: File | undefined,
  mode: string,
  strand: string,
  output: string,
  options: [],
  paramFile: string,
}


interface Node {
  children: Array<string>
  leaves: number
  assemblies?: number
  biosamples?: number
  experiments?: number
  local_samples?: number
  annotations?: number
}

export type Filter = {
  label: string
  placeholder?: string
  type: 'input' | 'select' | 'date'
  options?: Array<string>
  key: string
}

export interface SearchForm {
  filter: string
  filter_option: string
  sort_column: string
  sort_order: string
  start_date?: string
  end_date?: string
}

export interface OrganismSearchForm extends SearchForm {
  insdc_status: string
  goat_status: string
  parent_taxid: string
  bioproject: string
  target_list_status: string
  country: string
}


export interface AssemblySearchForm extends SearchForm {
  assembly_level: string
  submitter: string
}


export type ModelSearchForm = OrganismSearchForm | AssemblySearchForm

export interface TaxonNode extends Node {
  name: string
  rank: string
  taxid: string
}

export type BreadCrumb = {
  name: string
  path: string
}

export type TreeNode = {
  name: string
  rank: string
  taxid: string
  leaves: number
}

export type Contributor = {
  contributions?: number
  name: string
}

type Chromosome = {
  name: string
  size: number
}

export type Adapter = {
  type: 'RefGetAdapter'
  sequenceData: Record<string, Chromosome>
}

type Sequence = {
  type: 'ReferenceSequenceTrack'
  trackId: string
  name: string
  adapter: Adapter
}

export type GeneidFile = {
  extension:string,
  filename:string
}

export type AssemblyAdapter = {
  name: string
  sequence: Sequence
}

export type InfoBlock = {
  field: string,
  model: string,
  title: string,
  label?: string,
  type: 'pie' | 'dateline' | 'contribution' | 'list'
  isDate?: boolean
  isHabitat?: boolean
  color?: string
  class: string
}