<template>
  <UButton square icon="i-lucide-qr-code" variant="ghost" class="ml-1" size="xs" color="neutral" @click="open" />

  <UModal v-model:open="is_opened" title="QR Code" :close="true">
    <template #body>
      <section class="flex justify-center" ref="container"></section>

      <div class="flex justify-center grow mt-5">
        <UButton v-if="data" icon="i-lucide-download" variant="outline" size="xl" color="neutral" @click="do_save">{{ $t("qr.button_download") }}</UButton>
        <UButton v-if="data" icon="i-lucide-printer" variant="outline" size="xl" color="neutral" class="ml-3" @click="do_print">{{ $t("qr.button_print") }}</UButton>
      </div>
    </template>
  </UModal>
</template>
<script setup>
import qrcode from "qrcode-generator";
import { save } from 'save-file'

const props = defineProps({
  link: {
    type: String,
    required: true,
  },
})
const is_opened = ref(false);
const data = ref("");
const container = useTemplateRef("container");

function open() {
  is_opened.value = true;

  requestAnimationFrame(() => {
    const qr = qrcode(0, "H");
    qr.addData(props.link);
    qr.make();

    data.value = qr.createDataURL(10, 10);
    container.value.innerHTML = qr.createImgTag(10, 10);
  })
}

async function do_save() {
  save(data.value, "chronometer-qrcode.gif");
}

function do_print() {
  const w = window.open("", "QR Code");
  if (w) {
    w.document.write('<div style="display: flex; align-items: center; justify-content: center ;min-height: 100%; min-width: 100%;"><img src="' + data.value + '" onload="window.print()" /></div><style>@page { margin: 0; }</style>');
    w.document.close();
  }
}
</script>
