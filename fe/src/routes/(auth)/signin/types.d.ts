import { z } from 'zod';
import type { signInSchema } from './schema';

export type SignInPayload = z.infer<typeof signInSchema>;
