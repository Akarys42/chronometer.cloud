<template>
  <UTabs :items="[
    {
      label: 'Overview',
      slot: 'overview',
      icon: 'i-lucide-table',
    },
    {
      label: 'Origins',
      slot: 'origins',
      icon: 'i-lucide-globe',
    }
  ]">
    <template #list-leading>
      <UButton
          class="mr-1"
          icon="i-lucide-refresh-ccw"
          color="neutral"
          variant="outline"
          @click="fetch_data"
      >Refresh
      </UButton>
    </template>

    <template #overview>
      <UTable
          :data="data"
          :loading="loading"
          :columns="columns"
          v-model:sorting="sorting"
          v-model:column-filters="filter"
          class="flex-1"
      />
    </template>

    <template #origins>
      <USelect v-model="days_ago" class="mt-3" :items="[
        {
          label: 'Last 7 days',
          value: 7
        },
        {
          label: 'Last 14 days',
          value: 14
        },
        {
          label: 'Last 30 days',
          value: 30
        },
        {
          label: 'Last 90 days',
          value: 90
        },
      ]"/>

      <div class="mt-3" v-if="!loading && (origin_over_time_rum_analytics !== undefined)">
        <UCard
            v-for="(analytics, origin) in origin_over_time_rum_analytics"
            :key="origin"
            v-bind:analytics="analytics as any"
            v-bind:origin="origin as any as string"
        >
          <template #header>
            <div class="flex flex-col md:flex-row justify-between">
              <div>
                <p class="text-2xl md:text-5xl font-bold">
                  {{ origin }}
                </p>
              </div>
              <div class="hidden md:block pl-5 md:border-l-[3px] border-[var(--ui-border)]">
                <p class="text-xs text-muted uppercase mb-1.5">
                  Total Views
                </p>
                <p class="text-3xl text-highlighted font-semibold">
                  {{ format_data_for_vis(analytics).map(r => r.count).reduce((a, b) => a + b, 0) }}
                </p>
              </div>
              <div class="md:hidden text-sm flex flex-row">
                <p class="text-muted uppercase mr-1">
                  Total Views:
                </p>
                <p class="text-highlighted font-semibold">
                  {{ format_data_for_vis(analytics).map(r => r.count).reduce((a, b) => a + b, 0) }}
                </p>
              </div>
            </div>
          </template>

          <VisXYContainer :data="format_data_for_vis(analytics)">
            <VisLine
                :x="(_: DataRecord, i: number) => i"
                :y="(dataRecord: DataRecord) => dataRecord.count"
                color="var(--ui-primary)"
            />
            <VisArea
                :x="(_: DataRecord, i: number) => i"
                :y="(dataRecord: DataRecord) => dataRecord.count"
                color="var(--ui-primary)"
                :opacity="0.1"
            />
            <VisAxis type="x" :tick-format="(i: number) => format(subDays(new Date(), days_ago - i), 'd MMM')"/>
            <VisAxis type="y"/>
            <VisCrosshair
                color="var(--ui-primary)"
                :template="(dataRecord: DataRecord) => `${format(dataRecord.date, 'd MMM')}: ${dataRecord.count}`"
            />
            <VisTooltip/>
          </VisXYContainer>
        </UCard>
      </div>
      <USkeleton v-else class="m-5 w-max-full h-80"/>
    </template>
  </UTabs>

  <UModal title="Enter password" :open="data === undefined && !loading">
    <template #body>
      <div class="flex justify-center">
        <UFieldGroup>
          <UInput
              v-model:model-value="password"
              placeholder="Password"
              size="xl"
              :type="show_password ? 'text' : 'password'"
          >
            <template #trailing>
              <UButton
                  color="neutral"
                  variant="link"
                  size="sm"
                  :icon="show_password ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                  :aria-label="show_password ? 'Hide password' : 'Show password'"
                  :aria-pressed="show_password"
                  aria-controls="password"
                  @click="show_password = !show_password"
              />
            </template>
          </UInput>
          <UButton color="primary" size="xl" @click="fetch_data">
            Enter
          </UButton>
        </UFieldGroup>
      </div>
    </template>
  </UModal>

  <UModal title="Error" :open="wrong_password">
    <template #body>
      <div class="text-center">
        <p class="mb-4">The password you entered is incorrect. Please try again.</p>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type {TableColumn} from "#ui/components/Table.vue";
import type {Column, Row} from "@tanstack/table-core";
import {VisArea, VisAxis, VisCrosshair, VisLine, VisTooltip, VisXYContainer} from '@unovis/vue'
import {UButton, UDropdownMenu, UIcon} from "#components";
import {unique} from "~/utils";
import {eachDayOfInterval, format, interval, subDays} from "date-fns";

const backendUrl = useRuntimeConfig().public.backendUrl;

const data = ref(undefined);
const per_path_rum_analytics = ref(undefined);
const origin_over_time_rum_analytics = ref(undefined);
const days_ago = ref(14);

const password = ref("");
const show_password = ref(false);
const loading = ref(false);
const wrong_password = ref(false);
const sorting = ref([{
  id: 'last_modified',
  desc: true
}])

const filter = ref([{
  id: 'origin',
  value: [],
}]);

function getHeader(column: Column<any>, label: string) {
  const isSorted = column.getIsSorted()

  return h(
      UDropdownMenu as any,
      {
        content: {
          align: 'start'
        },
        'aria-label': 'Actions dropdown',
        items: [
          {
            label: 'Asc',
            type: 'checkbox',
            icon: 'i-lucide-arrow-up-narrow-wide',
            checked: isSorted === 'asc',
            onSelect: () => {
              if (isSorted === 'asc') {
                column.clearSorting()
              } else {
                column.toggleSorting(false)
              }
            }
          },
          {
            label: 'Desc',
            icon: 'i-lucide-arrow-down-wide-narrow',
            type: 'checkbox',
            checked: isSorted === 'desc',
            onSelect: () => {
              if (isSorted === 'desc') {
                column.clearSorting()
              } else {
                column.toggleSorting(true)
              }
            }
          }
        ]
      },
      () => h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        label,
        icon: isSorted
            ? isSorted === 'asc'
                ? 'i-lucide-arrow-up-narrow-wide'
                : 'i-lucide-arrow-down-wide-narrow'
            : 'i-lucide-arrow-up-down',
        class: '-mx-2.5 data-[state=open]:bg-elevated',
        'aria-label': `Sort by ${isSorted === 'asc' ? 'descending' : 'ascending'}`
      })
  )
}

function get_views(row: Row<any>): number {
  if (per_path_rum_analytics.value === undefined) {
    return 0;
  }

  const origin = (new URL(row.getValue<string>("origin"))).hostname;
  const public_link = "/" + row.getValue<string>("public_link");
  const private_link = "/" + row.getValue<string>("edit_link");
  const public_link_analytics = per_path_rum_analytics.value[origin]?.[public_link] || 0;
  const private_link_analytics = per_path_rum_analytics.value[origin]?.[private_link] || 0;
  return public_link_analytics + private_link_analytics;
}

const columns: TableColumn<any>[] = [
  {
    accessorKey: "name",
    header: ({column}) => getHeader(column, "Name"),
  },
  {
    accessorKey: "timers",
    header: ({column}) => getHeader(column, "Timers"),
    cell: ({row}) => {
      const count = (row.getValue<any[]>("timers") || []).length;
      return h(
          "span",
          {class: "flex"},
          [
            count.toString(),
            h(UIcon, {name: "i-lucide-alarm-clock", class: "inline-block ml-2 size-5"})
          ]
      );
    },
  },
  {
    accessorKey: "public_link",
    header: "Public Link",
    cell: ({row}) => {
      const link = row.getValue<string>("public_link");
      return h(
          "a",
          {
            href: link,
            target: "_blank",
            class: "dark:text-blue-300 text-blue-700 hover:underline break-all",
          },
          "/" + link
      );
    }
  },
  {
    accessorKey: "edit_link",
    header: "Edit Link",
    cell: ({row}) => {
      const link = row.getValue<string>("edit_link");
      return h(
          "a",
          {
            href: link,
            target: "_blank",
            class: "dark:text-blue-300 text-blue-700 hover:underline break-all",
          },
          "/" + link
      );
    }
  },
  {
    accessorKey: "last_modified",
    header: ({column}) => getHeader(column, "Last Modified"),
    cell: ({row}) => {
      return new Date(row.getValue("last_modified")).toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    }
  },
  {
    accessorKey: "origin",
    header: ({column}) => h(
        UDropdownMenu as any,
        {
          content: {
            align: 'start'
          },
          items: (data.value || []).map((item: any) => item.origin as string).filter(unique).map((origin: string) => ({
            label: origin,
            type: 'checkbox',
            checked: !(column.getFilterValue() as string[]).includes(origin),
            onUpdateChecked: (checked: boolean) => {
              if (checked) {
                column.setFilterValue(((v: string[]) => v.filter((ov: string) => ov !== origin)));
              } else {
                column.setFilterValue(((v: string[]) => [...v, origin]));
              }
            },
            onSelect(e: Event) {
              e.preventDefault();
            }
          }))
        },
        () => h(UButton, {
          color: 'neutral',
          variant: 'ghost',
          label: "Origin",
          icon: (column.getFilterValue() as string[]).length === 0 ? 'i-lucide-filter-x' : 'i-lucide-filter',
          class: '-mx-2.5 data-[state=open]:bg-elevated',
        })
    ),
    filterFn: (row: any, columnId: string, filterValue: string[]) => {
      return !filterValue.includes(row.getValue(columnId));
    },
  },
  {
    accessorKey: "views",
    header: ({column}) => getHeader(column, "Views"),
    cell: ({row}) => {
      if (per_path_rum_analytics.value === undefined) {
        return h(UIcon, {name: "i-lucide-loader-circle", class: "inline-block animate-spin size-5"});
      }

      const analytics = get_views(row);

      if (analytics === 0) {
        return "No data";
      } else {
        return h(
            "span",
            {class: "flex"},
            [
              analytics.toString(),
              h(UIcon, {name: "i-lucide-eye", class: "inline-block ml-2 size-5"})
            ]
        );
      }
    },
    sortingFn: (rowA: Row<any>, rowB: Row<any>) => {
      if (per_path_rum_analytics.value === undefined) {
        return 0;
      }

      return get_views(rowA) - get_views(rowB);
    }
  }
]

type DataRecord = {
  date: Date,
  count: number
}

function format_data_for_vis(data: any): DataRecord[] {
  const dates = eachDayOfInterval(interval(subDays(new Date(), days_ago.value), new Date()));

  return dates.map(date => {
    const date_str = date.toISOString().split("T")[0];

    return {
      date: date,
      count: data[date_str!] || 0
    }
  });
}

async function fetch_data(): Promise<void> {
  loading.value = true;

  const json = await fetch(backendUrl + "/admin/index", {
    headers: {
      "Authorization": "Plain " + password.value
    }
  })
      .then(async r => {
        loading.value = false;

        if (r.status == 401) {
          wrong_password.value = true;
        } else {
          const json = await r.json();
          data.value = json;
          return json;
        }
      })

  const hosts = json.map((item: any) => item.origin)
      .map((origin: string) => (new URL(origin).hostname))
      .filter(unique)
      .filter((host: string) => host !== "")
      .join(",")

  await fetch(backendUrl + "/admin/rum_analytics?hosts=" + hosts, {
    headers: {
      "Authorization": "Plain " + password.value
    }
  }).then(async r => {
    if (r.status == 200) {
      const analytics = await r.json()
      per_path_rum_analytics.value = analytics.per_path;
      origin_over_time_rum_analytics.value = analytics.origin_over_time;
    }
  });
}
</script>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
