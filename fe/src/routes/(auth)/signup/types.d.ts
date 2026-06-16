import { z } from 'zod';
import type { signUpSchema } from './schema';

export type SignUpPayload = z.infer<typeof signUpSchema>;
