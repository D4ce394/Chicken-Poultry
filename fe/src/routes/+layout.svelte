<script lang="ts">
	import '../styles/app.css';
	import { Toaster } from 'svelte-french-toast';
	import { QueryClientProvider } from '@tanstack/svelte-query';
	import { queryClient } from '$lib/queryClient';
  </script>
  
  <QueryClientProvider client={queryClient}>
	<Toaster />
	<slot />
  </QueryClientProvider>
  