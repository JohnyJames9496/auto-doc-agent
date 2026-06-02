import { Pool } from 'pg';
import * as fs from 'fs';
import * as path from 'path';

const pool = new Pool({
    connectionString: process.env.DATABASE_URL_DIRECT,
    ssl: { rejectUnauthorized: false },
});

async function generateDocPages() {
    const client = await pool.connect();
    try {
        const { rows } = await client.query(`
            SELECT DISTINCT ON (d.project_id, d.file_path, d.function_name)
                d.project_id,
                p.name as project_name,
                d.file_path,
                d.function_name,
                d.doc_content,
                d.language,
                d.updated_at
            FROM documentation d
            JOIN projects p ON p.id = d.project_id
            ORDER BY d.project_id, d.file_path, d.function_name, d.updated_at DESC
        `);

        if (rows.length === 0) {
            console.log('No documentation found in database.');
            const outputDir = path.join('docs', 'generated');
            fs.mkdirSync(outputDir, { recursive: true });
            fs.writeFileSync(
                path.join(outputDir, 'intro.md'),
                `---\ntitle: Introduction\n---\n\n# Auto-Doc Agent\n\nDocumentation will appear here automatically as you write code.\n`
            );
            return;
        }

        const byFile = new Map<string, typeof rows>();
        for (const row of rows) {
            const key = `${row.project_name}:${row.file_path}`;
            if (!byFile.has(key)) byFile.set(key, []);
            byFile.get(key)!.push(row);
        }

        for (const [key, docs] of byFile) {
            const [projectName, filePath] = key.split(':');
            const fileName = path.basename(filePath, path.extname(filePath));
            const safeProjectName = projectName.replace(/[^a-zA-Z0-9-_]/g, '-').toLowerCase();
            const outputDir = path.join('docs', 'generated', safeProjectName);
            fs.mkdirSync(outputDir, { recursive: true });

            const content = [
                `---`,
                `title: ${fileName}`,
                `sidebar_label: ${fileName}`,
                `---`,
                ``,
                `# \`${filePath}\``,
                ``,
                `*Last updated: ${new Date(docs[0].updated_at).toLocaleDateString()}*`,
                ``,
                ...docs.map(d => d.doc_content),
            ].join('\n');

            fs.writeFileSync(path.join(outputDir, `${fileName}.md`), content);
            console.log(`Generated: ${outputDir}/${fileName}.md`);
        }

        console.log(`Done — ${rows.length} documentation entries across ${byFile.size} files`);
    } finally {
        client.release();
        await pool.end();
    }
}

generateDocPages().catch(console.error);
