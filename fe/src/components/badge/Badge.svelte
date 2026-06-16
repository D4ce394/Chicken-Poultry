<script lang="ts">
	import type { BadgeType } from "./types";

    export let type: BadgeType;
    export let text: string;
</script>

<span
	class={
        `inline-flex items-center justify-center gap-1 rounded-full py-0.5 pl-2 pr-2.5 text-sm font-medium 
        ${type == 'primary' ? 'bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400' : type == 'success' ? 'bg-success-50 text-success-500 dark:bg-success-500/15 dark:text-success-400' : type == 'warning' ? 'bg-warning-50 text-warning-500 dark:bg-warning-500/15 dark:text-warning-400' : type == 'error' ? 'bg-error-50 text-error-500 dark:bg-error-500/15 dark:text-error-400' : type == 'info' ? 'bg-info-50 text-info-500 dark:bg-info-500/15 dark:text-info-400' : type == 'dark' ? 'bg-gray-800 text-white' : ''} 
        `
    }
>
	{text}
</span>
