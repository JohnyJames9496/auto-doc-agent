import * as vscode from 'vscode';

export class AutoDocHoverProvider implements vscode.HoverProvider {
    private docs = new Map<string, Map<string, string>>();

    setDocumentation(filePath: string, functionName: string, markdown: string) {
        if (!this.docs.has(filePath)) {
            this.docs.set(filePath, new Map());
        }
        this.docs.get(filePath)!.set(functionName, markdown);
    }

    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
    ): vscode.Hover | undefined {
        const wordRange = document.getWordRangeAtPosition(position, /[\w]+/);
        if (!wordRange) return;

        const word = document.getText(wordRange);
        const fileDocs = this.docs.get(document.uri.fsPath);
        if (!fileDocs) return;

        const docContent = fileDocs.get(word);
        if (!docContent) return;

        const markdown = new vscode.MarkdownString(docContent);
        markdown.isTrusted = true;

        return new vscode.Hover(markdown, wordRange);
    }
}
