import { buildApp } from "./app.js";

const port = Number(process.env.PORT ?? 4000);
const host = process.env.HOST ?? "0.0.0.0";

const app = await buildApp({ logger: process.env.NODE_ENV !== "test" });

try {
  await app.listen({ port, host });
  console.log(`SignBridge backend listening on ${host}:${port}`);
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
