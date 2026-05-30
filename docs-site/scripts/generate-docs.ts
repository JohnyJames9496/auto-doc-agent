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
            SELECT DISTINCT ON (project_id, file_path, function_name)
                project_id,
                file_path,
                function_name,
                doc_content,
                language,
                updated_at
            FROM documentation
            ORDER BY project_id, file_path, function_name, updated_at DESC
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
            const key = `${row.project_id}:${row.file_path}`;
            if (!byFile.has(key)) byFile.set(key, []);
            byFile.get(key)!.push(row);
        }

        for (const [key, docs] of byFile) {
            const [projectId, filePath] = key.split(':');
            const fileName = path.basename(filePath, path.extname(filePath));
            const outputDir = path.join('docs', 'generated', projectId);
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
