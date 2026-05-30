"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CodeChangeDetector = void 0;
const vscode = __importStar(require("vscode"));
class CodeChangeDetector {
    client;
    hoverProvider;
    debounceTimer;
    lastVersionMap = new Map();
    constructor(client, hoverProvider) {
        this.client = client;
        this.hoverProvider = hoverProvider;
    }
    start(context) {
        const disposable = vscode.workspace.onDidChangeTextDocument((event) => {
            const config = vscode.workspace.getConfiguration('autoDocAgent');
            if (!config.get('enabled', true))
                return;
            if (event.document.uri.scheme !== 'file')
                return;
            clearTimeout(this.debounceTimer);
            const debounceMs = config.get('debounceMs', 3000);
            this.debounceTimer = setTimeout(() => this.processDocument(event.document), debounceMs);
        });
        context.subscriptions.push(disposable);
    }
    async processDocument(document) {
        const lastVersion = this.lastVersionMap.get(document.uri.toString()) ?? -1;
        if (document.version <= lastVersion)
            return;
        const language = document.languageId;
        const functions = this.extractFunctions(document.getText(), language);
        if (functions.length === 0)
            return;
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
        const projectId = workspaceFolder?.name ?? 'default';
        for (const fn of functions) {
            const taskId = await this.client.requestDocumentation({
                file_path: document.uri.fsPath,
                function_name: fn.name,
                code_snippet: fn.code,
                language,
                project_id: projectId,
            });
            if (taskId) {
                this.pollForResult(taskId, fn.name, document.uri.fsPath);
            }
        }
        this.lastVersionMap.set(document.uri.toString(), document.version);
    }
    extractFunctions(text, language) {
        const results = [];
        const lines = text.split('\n');
        if (language === 'python') {
            for (let i = 0; i < lines.length; i++) {
                const match = lines[i].match(/^(?:async\s+)?def\s+(\w+)\s*\(/);
                if (!match)
                    continue;
                const fnName = match[1];
                const indent = lines[i].match(/^(\s*)/)?.[1].length ?? 0;
                let j = i + 1;
                while (j < lines.length) {
                    const lineIndent = lines[j].match(/^(\s*)/)?.[1].length ?? 0;
                    if (lines[j].trim() && lineIndent <= indent)
                        break;
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
                const match = lines[i].match(/(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\()/);
                if (!match)
                    continue;
                const fnName = match[1] || match[2];
                if (!fnName)
                    continue;
                let braceCount = 0;
                let started = false;
                let j = i;
                while (j < lines.length && j < i + 100) {
                    for (const ch of lines[j]) {
                        if (ch === '{') {
                            braceCount++;
                            started = true;
                        }
                        if (ch === '}')
                            braceCount--;
                    }
                    j++;
                    if (started && braceCount === 0)
                        break;
                }
                if (started && braceCount === 0) {
                    const fnCode = lines.slice(i, j).join('\n');
                    results.push({ name: fnName, code: fnCode, line: i });
                }
            }
        }
        return results;
    }
    pollForResult(taskId, fnName, filePath, attempts = 0) {
        if (attempts > 15)
            return;
        setTimeout(async () => {
            const result = await this.client.pollTaskResult(taskId);
            if (result?.status === 'complete' && result.documentation) {
                this.hoverProvider.setDocumentation(filePath, fnName, result.documentation);
            }
            else if (result?.status === 'pending') {
                this.pollForResult(taskId, fnName, filePath, attempts + 1);
            }
        }, 2000);
    }
    async generateForCurrentFile() {
        const editor = vscode.window.activeTextEditor;
        if (!editor)
            return;
        await this.processDocument(editor.document);
    }
    stop() {
        clearTimeout(this.debounceTimer);
    }
}
exports.CodeChangeDetector = CodeChangeDetector;
//# sourceMappingURL=codeDetector.js.map