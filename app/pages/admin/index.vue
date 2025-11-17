<template>
  <div v-if="(data !== undefined || loading) && !wrong_password">
    <UButton
        class="mb-3"
        icon="i-lucide-refresh-ccw"
        color="neutral"
        variant="outline"
        @click="fetch_data"
    >Refresh
    </UButton>
    <UTable
        :data="data"
        :loading="loading"
        :columns="columns"
        v-model:sorting="sorting"
        v-model:column-filters="filter"
        class="flex-1"
    />
  </div>
  <USkeleton v-else class="m-5 w-max-full h-full"/>

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
import type {Column} from "@tanstack/table-core";
import {UButton, UDropdownMenu, UIcon} from "#components";
import {unique} from "~/utils";

const backendUrl = useRuntimeConfig().public.backendUrl;

const password = ref("");
const show_password = ref(false);
const data = ref(undefined);
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
  }
]

async function fetch_data(): Promise<void> {
  loading.value = true;

  await fetch(backendUrl + "/admin/index", {
    headers: {
      "Authorization": "Plain " + password.value
    }
  })
      .then(async r => {
        loading.value = false;

        if (r.status == 401) {
          wrong_password.value = true;
        } else {
          data.value = await r.json();
        }
      })
}
</script>
