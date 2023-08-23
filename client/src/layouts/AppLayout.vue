<template>
  <div class="app-layout">
    <navbar class="app-layout__navbar" />
    <div class="app-layout__content">
      <div class="app-layout__page">
        <div id="scroll-container" class="layout fluid">
          <router-view v-slot="{ Component }">
            <Transition name="fade">
              <component :is="Component" />
            </Transition>
          </router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { onBeforeRouteUpdate } from 'vue-router'
import { useGlobalStore } from '../stores/global-store'
import Login from '../components/modals/Login.vue'
import Navbar from '../components/navbar/Navbar.vue'
import Sidebar from '../components/sidebar/Sidebar.vue'



const GlobalStore = useGlobalStore()


const mobileBreakPointPX = 480
const tabletBreakPointPX = 768

const sidebarWidth = ref('100wv')
const sidebarMinimizedWidth = ref(undefined)

const isMobile = ref(false)
const isTablet = ref(false)
const { isSidebarMinimized } = storeToRefs(GlobalStore)
const checkIsTablet = () => window.innerWidth <= tabletBreakPointPX
const checkIsMobile = () => window.innerWidth <= mobileBreakPointPX

const onResize = () => {
  isSidebarMinimized.value = checkIsTablet()

  isMobile.value = checkIsMobile()
  isTablet.value = checkIsTablet()
  sidebarMinimizedWidth.value = isMobile.value ? '0' : '4.5rem'
  sidebarWidth.value = isTablet.value ? '100%' : '16rem'
}

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})

onBeforeRouteUpdate(() => {
  if (checkIsTablet()) {
    // Collapse sidebar after route change for Mobile
    isSidebarMinimized.value = true
  }
})

onResize()


</script>

<style lang="scss">
$mobileBreakPointPX: 480px;
$tabletBreakPointPX: 768px;

.page-wrapper {
  padding: 2rem;
}

.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;

  &__navbar {
    min-height: 4rem;
  }

  &__content {
    display: flex;
    height: calc(100vh - 4rem);
    flex: 1;

    @media screen and (max-width: $tabletBreakPointPX) {
      height: calc(100vh - 6.5rem);
    }

  }

  &__page {
    flex-grow: 2;
    overflow-y: scroll;
  }
}

.chart {
  height: 400px;
}

.row-equal .flex {
  .va-card {
    height: 100%;
  }
}</style>
