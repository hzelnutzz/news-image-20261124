// make.fun news-image entry for 24 November 2026.
// Writes the agent-drawn broadsheet front page (entry.png) to the output dir.
import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = join(import.meta.dirname, 'entry.png');
const target = join(outputDir, 'entry.png');

copyFileSync(source, target);
console.log(`wrote ${target}`);
