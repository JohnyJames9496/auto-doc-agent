import * as vscode from 'vscode';
import { AutoDocClient } from './apiClient';
import { AutoDocHoverProvider } from './hoverProvider';

interface FunctionInfo {
    name: string;
    code: string;
    line: number;
}

export class CodeChangeDetector {
    private debounceTimer: NodeJS.Timeout | undefined;
    private lastVersionMap = new Map<string, number>();

    constructor(
        private client: AutoDocClient,
        private hoverProvider: AutoDocHoverProvider,
    ) {}

    start(context: vscode.ExtensionContext) {
        const disposable = vscode.workspace.onDidChangeTextDocument((event) => {
            const config = vscode.workspace.getConfiguration('autoDocAgent');
            if (!config.get<boolean>('enabled', true)) return;
            if (event.document.uri.scheme !== 'file') return;

            clearTimeout(this.debounceTimer);

            const debounceMs = config.get<number>('debounceMs', 3000);
            this.debounceTimer = setTimeout(
                () => this.processDocument(event.document),
                debounceMs,
            );
        });

        context.subscriptions.push(disposable);
    }

    async processDocument(document: vscode.TextDocument) {
        const lastVersion = this.lastVersionMap.get(document.uri.toString()) ?? -1;
        if (document.version <= lastVersion) return;

        const language = document.languageId;
        const functions = this.extractFunctions(document.getText(), language);
        if (functions.length === 0) return;

        const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
        const projectId = workspaceFolder?.name ?? 'default';

        for (const fn of functions) {
            const result = await this.client.requestDocumentation({
                file_path: document.uri.fsPath,
                function_name: fn.name,
                code_snippet: fn.code,
                language,
                project_id: projectId,
            });

            // If cached/complete, set immediately
            if (result.documentation) {
                this.hoverProvider.setDocumentation(document.uri.fsPath, fn.name, result.documentation);
            } else if (result.taskId) {
                // Otherwise poll for result
                this.pollForResult(result.taskId, fn.name, document.uri.fsPath);
            }
        }

        this.lastVersionMap.set(document.uri.toString(), document.version);
    }

    private extractFunctions(text: string, language: string): FunctionInfo[] {
        const results: FunctionInfo[] = [];
        const lines = text.split('\n');

        if (language === 'python') {
            for (let i = 0; i < lines.length; i++) {
                const match = lines[i].match(/^(?:async\s+)?def\s+(\w+)\s*\(/);
                if (!match) continue;

                const fnName = match[1];
                const indent = lines[i].match(/^(\s*)/)?.[1].length ?? 0;

                let j = i + 1;
                while (j < lines.length) {
                    const lineIndent = lines[j].match(/^(\s*)/)?.[1].length ?? 0;
                    if (lines[j].trim() && lineIndent <= indent) break;
                    j++;
                }

                if (j > i + 1) {
                    const fnCode = lines.slice(i, Math.min(j, i + 100)).join('\n');
                    results.push({ name: fnName, code: fnCode, line: i });
                }
            }
        }

        if (language === 'typescript' || language === 'javascript') {
            for (let i = 0; i < lines.length; i++) {
                const match = lines[i].match(
                    /(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\()/
                );
                if (!match) continue;

                const fnName = match[1] || match[2];
                if (!fnName) continue;

                let braceCount = 0;
                let started = false;
                let j = i;

                while (j < lines.length && j < i + 100) {
                    for (const ch of lines[j]) {
                        if (ch === '{') { braceCount++; started = true; }
                        if (ch === '}') braceCount--;
                    }
                    j++;
                    if (started && braceCount === 0) break;
                }

                if (started && braceCount === 0) {
                    const fnCode = lines.slice(i, j).join('\n');
                    results.push({ name: fnName, code: fnCode, line: i });
                }
            }
        }

        return results;
    }

    private pollForResult(taskId: string, fnName: string, filePath: string, attempts = 0) {
        if (attempts > 15) return;

        setTimeout(async () => {
            const result = await this.client.pollTaskResult(taskId);
            if (result?.status === 'complete' && result.documentation) {
                this.hoverProvider.setDocumentation(filePath, fnName, result.documentation);
            } else if (result?.status === 'pending') {
                this.pollForResult(taskId, fnName, filePath, attempts + 1);
            }
        }, 2000);
    }

    async generateForCurrentFile() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;
        await this.processDocument(editor.document);
    }

    stop() {
        clearTimeout(this.debounceTimer);
    }
}