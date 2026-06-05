import * as vscode from 'vscode';

interface DocEntry {
    content: string;
    timestamp: number;
}

export class AutoDocHoverProvider implements vscode.HoverProvider {
    // Bug #1 fix — store timestamp with each entry
    private docs = new Map<string, Map<string, DocEntry>>();
    private readonly TTL_MS = 60 * 60 * 1000; // 1 hour

    setDocumentation(filePath: string, functionName: string, markdown: string) {
        if (!this.docs.has(filePath)) {
            this.docs.set(filePath, new Map());
        }
        this.docs.get(filePath)!.set(functionName, {
            content: markdown,
            timestamp: Date.now(),
        });
    }

    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
    ): vscode.Hover | undefined {
        // Bug #4 fix — error handling
        try {
            const wordRange = document.getWordRangeAtPosition(position, /[\w]+/);
            if (!wordRange) return;

            const word = document.getText(wordRange);

            // Bug #2 fix — only show for function definitions/calls
            const lineText = document.lineAt(position.line).text;
            const wordEnd = wordRange.end.character;
            const nextChar = lineText[wordEnd];
            const isFunction =
                nextChar === '(' ||
                lineText.trimStart().startsWith('def ') ||
                lineText.trimStart().startsWith('function ') ||
                lineText.trimStart().startsWith('async def ');

            if (!isFunction) return;

            const fileDocs = this.docs.get(document.uri.fsPath);
            if (!fileDocs) return;

            const entry = fileDocs.get(word);
            if (!entry) return;

            // Bug #1 fix — check TTL
            if (Date.now() - entry.timestamp > this.TTL_MS) {
                fileDocs.delete(word);
                return;
            }

            const markdown = new vscode.MarkdownString(entry.content);
            markdown.isTrusted = true;
            return new vscode.Hover(markdown, wordRange);

        } catch (error) {
            console.error('AutoDoc hover error:', error);
            return undefined;
        }
    }

    // Bug #5 fix — cleanup methods
    clearFile(filePath: string) {
        this.docs.delete(filePath);
    }

    dispose() {
        this.docs.clear();
    }
}