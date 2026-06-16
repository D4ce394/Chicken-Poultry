import adapterAuto from '@sveltejs/adapter-auto';
import adapterNode from '@sveltejs/adapter-node';
import adapterStatic from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const target = process.env.BUILD_TARGET;

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter:
			target === 'firebase'
				? adapterStatic({ fallback: 'index.html' })
				: target === 'node'
				? adapterNode()
				: adapterAuto() // default: auto-detect (Vercel, Netlify, dll)
	}
};

export default config;
