import adapterNode from '@sveltejs/adapter-node';
import adapterStatic from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const isFirebase = process.env.BUILD_TARGET === 'firebase';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter: isFirebase
			? adapterStatic({ fallback: 'index.html' })
			: adapterNode()
	}
};

export default config;
