<script lang="ts">
	import Sidebar from '../../components/sidebar/Sidebar.svelte';
	import Header from '../../components/header/Header.svelte';
	import { queryClient } from '$lib/queryClient';
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import HasAuth from '../../viewports/HasAuth.svelte';
  
	let { children } = $props();
	let sidebarToggle = false;
	let menuToggle = false;
  </script>
  
  <QueryClientProvider client={queryClient}>
	<HasAuth>
	  <div class="flex h-screen overflow-hidden">
		<Sidebar sidebarToggle={sidebarToggle} />
		<div class="relative flex flex-1 flex-col overflow-x-hidden overflow-y-auto">
		  <Header sidebarToggle={sidebarToggle} menuToggle={menuToggle} />
		  <main>
			<div class="mx-auto max-w-(--breakpoint-2xl) p-4 md:p-6">
			  {@render children()}
			</div>
		  </main>
		</div>
	  </div>
	</HasAuth>
  </QueryClientProvider>
  