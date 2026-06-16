// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		//
	}
	interface User {
		id: string;
		name: string;
		username: string;
		email: string;
		password: string;
		created_at: string;
		updated_at: string;
	}
}

export {};
