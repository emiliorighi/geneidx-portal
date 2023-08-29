<template>
    <div ref="transcripts">

    </div>
</template>
<script lang="ts" setup>
import IsoformTrackViewer from '../../viz/IsoformTrackViewer'
import * as d3 from 'd3'
import { onMounted, ref } from 'vue'

const transcripts = ref()

onMounted(() => {
    transcriptTracks(config)
})

const testGene = {
    "exons": {
        "ENST00000311595.9": [{
            "chrom": "17",
            "chromEnd": 77071172,
            "exonId": "ENSE00002713933.1",
            "exonNumber": "1",
            "chromStart": 77071151,
            "strand": "+"
        },
        {
            "chrom": "17",
            "chromEnd": 77073579,
            "exonId": "ENSE00003672628.1",
            "exonNumber": "2",
            "chromStart": 77073512,
            "strand": "+"
        },
        {
            "chrom": "17",
            "chromEnd": 77073946,
            "exonId": "ENSE00003475281.1",
            "exonNumber": "3",
            "chromStart": 77073745,
            "strand": "+"
        },
        {
            "chrom": "17",
            "chromEnd": 77075719,
            "exonId": "ENSE00001111713.1",
            "exonNumber": "4",
            "chromStart": 77075571,
            "strand": "+"
        },
        {
            "chrom": "17",
            "chromEnd": 77076446,
            "exonId": "ENSE00003651250.1",
            "exonNumber": "5",
            "chromStart": 77076289,
            "strand": "+"
        },
        {
            "chrom": "17",
            "chromEnd": 77077155,
            "exonId": "ENSE00003607773.1",
            "exonNumber": "6",
            "chromStart": 77077007,
            "strand": "+"
        },
        {
            "chrom": "17",
            "chromEnd": 77078612,
            "exonId": "ENSE00002720924.1",
            "exonNumber": "7",
            "chromStart": 77077980,
            "strand": "+"
        }
        ]
    },
    "transcripts": [{
        "chromosome": "17",
        "end": 77078612,
        "gencodeId": "ENSG00000167280.12",
        "geneSymbol": "ENGASE",
        "start": 77071151,
        "strand": "+",
        "transcriptId": "ENST00000311595.9"
    }]
}
const config = {
    id: 'userTranscripts',
    data: testGene,
    width: 600,
    height: 80,
    marginLeft: 100,
    marginRight: 20,
    marginTop: 0,
    marginBottom: 20,
    labelPos: 'left'
}

function transcriptTracks(config) {
    const margin = {
        top: config.marginTop,
        right: config.marginRight,
        bottom: config.marginBottom,
        left: config.marginLeft
    };
    const inWidth = config.width - (config.marginLeft + config.marginRight);
    const inHeight = config.height - (config.marginTop + config.marginBottom);

    const svg = d3.select(transcripts.value)
        .append('svg')
        .attr("width", config.width)
        .attr("height", config.height)
        .append("g")
        .attr("transform", `translate(${config.marginLeft}, ${config.marginTop})`)

    const tooltip = svg
        .append("div")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "2px")
        .style("border-radius", "5px")
        .style("padding", "5px")
        
    const mouseover = function (d) {
        tooltip
            .style("opacity", 1)
        d3.select(this)
            .style("stroke", "black")
            .style("opacity", 1)
    }
    const mousemove = function (d) {
        tooltip
            .html("The exact value of<br>this cell is: " + d.value)
            .style("left", (d3.mouse(this)[0] + 70) + "px")
            .style("top", (d3.mouse(this)[1]) + "px")
    }
    const mouseleave = function (d) {
        tooltip
            .style("opacity", 0)
        d3.select(this)
            .style("stroke", "none")
            .style("opacity", 0.8)
    }
    d3.selectAll('.exon')
        .on('mouseover', mouseover)
        .on('mousemove', mousemove)
        .on('mouseleave', mouseleave)
    // render the transcripts
    // let tooltipId = `${config.id}Tooltip`;
    const confs = {
        x: 0,
        y: 0,
        w: inWidth,
        h: inHeight,
        labelOn: config.labelPos
    };
    let viewer = new IsoformTrackViewer(config.data.transcripts, config.data.exons, undefined, confs);
    viewer.render(false, svg, config.labelPos);

}
</script>
<style>
.intron {
    stroke: rgb(85, 95, 102);
    stroke-width: 1px;
    /*stroke-dasharray: 10,5;*/
}

.exon {
    stroke: rgb(75, 134, 153);
    fill: red;
    stroke-width: 1px;
    stroke-dasharray: 0.9;
}

.exon-curated {
    cursor: pointer;
    stroke-width: 2px;
    stroke: rgb(85, 95, 102);
}
</style>