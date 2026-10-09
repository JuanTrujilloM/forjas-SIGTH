<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { OrgChartEmployee } from '@/types/employee.types'

// main code
const props = defineProps<{
  employee: OrgChartEmployee
  childrenOf: (id: number) => OrgChartEmployee[]
  depth: number
  isRoot?: boolean
  expandAll: { open: boolean; version: number } | null
}>()

const team = computed(() => props.childrenOf(props.employee.id))
const isOpen = ref(props.depth < 2)

watch(
  () => props.expandAll?.version,
  () => {
    if (props.expandAll) {
      isOpen.value = props.expandAll.open
    }
  },
)
</script>

<template>
  <li class="org-node">
    <div class="org-card d-inline-flex align-items-center gap-2 border rounded bg-body px-2 py-1">
      <img
        v-if="employee.photo_thumbnail"
        class="rounded object-fit-cover flex-shrink-0"
        :src="employee.photo_thumbnail"
        alt=""
        width="32"
        height="40"
        loading="lazy"
      />
      <span
        v-else-if="'photo_thumbnail' in employee"
        class="rounded bg-light border flex-shrink-0"
        style="width: 32px; height: 40px"
        aria-hidden="true"
      ></span>

      <div class="lh-sm">
        <RouterLink :to="{ name: 'employee-detail', params: { id: employee.id } }">
          {{ employee.full_name }}
        </RouterLink>
        <div class="small text-secondary">
          {{ employee.position_name ?? '—' }} · {{ employee.section_name ?? '—' }}
        </div>
        <div v-if="isRoot && employee.immediate_boss_name" class="small text-body-tertiary">
          Reporta a {{ employee.immediate_boss_name }}
        </div>
      </div>

      <button
        v-if="team.length"
        class="btn btn-sm btn-outline-secondary ms-1"
        type="button"
        :aria-expanded="isOpen"
        :aria-label="`${isOpen ? 'Ocultar' : 'Mostrar'} el equipo de ${employee.full_name}`"
        @click="isOpen = !isOpen"
      >
        {{ isOpen ? '−' : '+' }} {{ team.length }}
      </button>
    </div>

    <ul v-if="isOpen && team.length" class="org-tree">
      <OrgChartNode
        v-for="member in team"
        :key="member.id"
        :employee="member"
        :children-of="childrenOf"
        :depth="depth + 1"
        :expand-all="expandAll"
      />
    </ul>
  </li>
</template>

<style scoped>
.org-tree {
  list-style: none;
  margin: 0 0 0 1rem;
  padding-left: 1.5rem;
  border-left: 1px solid var(--bs-border-color);
}

.org-node {
  position: relative;
  padding-top: 0.5rem;
}

.org-tree > .org-node::before {
  content: '';
  position: absolute;
  top: 1.75rem;
  left: -1.5rem;
  width: 1.25rem;
  border-top: 1px solid var(--bs-border-color);
}

.org-card {
  max-width: 100%;
}
</style>
