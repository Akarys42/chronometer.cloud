export default defineNuxtPlugin(() => {
	const locale = localStorage.getItem('locale')

	if (locale) {
		const nuxtApp = useNuxtApp()
		nuxtApp.$i18n.setLocale(locale as any)
	}
})
