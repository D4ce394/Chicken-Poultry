import * as zod from 'zod';

export const signInSchema = zod.object({
	email: zod.string().email({ message: 'Invalid email address' }),
	password: zod.string().min(8, { message: 'Password must be at least 8 characters long' })
});
