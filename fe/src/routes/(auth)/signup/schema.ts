import * as zod from 'zod';

export const signUpSchema = zod.object({
	name: zod.string().min(1, { message: 'Name is required' }),
	email: zod.string().email({ message: 'Invalid email address' }),
	password: zod
		.string()
		.min(8, { message: 'Password must be at least 8 characters long' })
		.regex(/[a-z]/, { message: 'Password must contain at least one lowercase letter' })
		.regex(/[A-Z]/, { message: 'Password must contain at least one uppercase letter' })
		.regex(/[0-9]/, { message: 'Password must contain at least one number' })
		.regex(/[^a-zA-Z0-9]/, { message: 'Password must contain at least one special character' })
});
