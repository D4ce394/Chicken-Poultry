<script lang="ts">
	import { onMount } from 'svelte';

	onMount(() => {
		const auth = localStorage.getItem('accessToken');

		if (!auth) {
			window.location.href = '/signin';
		}
	});
</script>

<slot />
