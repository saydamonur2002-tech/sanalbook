import { defineCollection, reference, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { telifDenetle } from './lib/telif';

const kisaAd = z
  .string()
  .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Kısa ad küçük harf, rakam ve kısa çizgiden oluşur.');

const countries = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/countries' }),
  schema: z.object({
    name: z.string().min(1),
    slug: kisaAd,
    order: z.number().int().positive(),
    description: z.string().min(1),
  }),
});

const categories = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/categories' }),
  schema: z.object({
    name: z.string().min(1),
    slug: kisaAd,
    country: reference('countries'),
    order: z.number().int().positive(),
    description: z.string().min(1),
  }),
});

/**
 * Eser kaydı telif kuralını taşır. Çevirmen yoksa her iki alan da null olur
 * ve sitede "yok" diye gösterilir. Serbest olmayan kayıt derlemeyi durdurur.
 */
const works = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/works' }),
  schema: z
    .object({
      title: z.string().min(1),
      slug: kisaAd,
      author: z.string().min(1),
      authorDeathYear: z.number().int(),
      translator: z.string().nullable(),
      translatorDeathYear: z.number().int().nullable(),
      country: reference('countries'),
      category: reference('categories'),
      order: z.number().int().positive(),
      sourceName: z.string().min(1),
      sourceUrl: z.string().url(),
      sourceRevision: z.number().int().positive(),
      sourceRetrieved: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
      originalPublication: z.string().nullable(),
      sourceNote: z.string().min(1).optional(),
      /** Boş bırakılır. Seri gruplaması yapılmaz. */
      seri: z.string().nullable().optional(),
    })
    .superRefine((eser, ctx) => {
      const sonuc = telifDenetle(eser);
      if (!sonuc.serbest) {
        for (const hata of sonuc.hatalar) {
          ctx.addIssue({ code: 'custom', message: `TELİF: ${hata}` });
        }
      }
    }),
});

const chapters = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/chapters' }),
  schema: z.object({
    title: z.string().min(1),
    work: reference('works'),
    order: z.number().int().positive(),
  }),
});

export const collections = { countries, categories, works, chapters };
