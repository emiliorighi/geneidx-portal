<template>
    <div>
        <Hero />
        <Pipeline />
        <!-- <Logos/> -->
        <Annotations />
        <Taxonomy />
        <section class="row">
            <div class="flex">
                <h2 class="va-h1">
                    Genome Browser
                </h2>
                <p>
                    Visualize the annotated species in the genome browser and compare with your custom annotation
                </p>
            </div>

            <div class="flex">
                <va-card>

                </va-card>
            </div>
        </section>
    </div>
    <!-- 
            geneid description and repo > geneid form page
            geneid+blastx description and repo > geneidx form page
            annotated species > species page > species details 
            tanomy explorer > taxonomy page - charts/closer species/ > species details
            genome browser > multiple browser page - uplaod your custom annotation
         -->
</template>
<script setup lang="ts">
import Hero from '../../components/landing/Hero.vue'
import Pipeline from '../../components/landing/Pipeline.vue'
import Logos from '../../components/landing/Logos.vue'
import Annotations from '../../components/landing/Annotations.vue'
import Taxonomy from '../../components/landing/Taxonomy.vue'

</script>
<style scoped></style>