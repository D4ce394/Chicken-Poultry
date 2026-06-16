<script lang="ts">
	export let pageName: string;
</script>

<div class="flex flex-wrap items-center justify-between gap-3">
	<h2 class="text-xl font-semibold text-gray-800 dark:text-white/90">{pageName}</h2>

	<nav>
		<ol class="flex items-center gap-1.5">
			<li class="text-sm text-gray-800 dark:text-white/90">{pageName}</li>
		</ol>
	</nav>
</div>
