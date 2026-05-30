import * as vscode from 'vscode';
import { AutoDocClient } from './apiClient';
import { AutoDocHoverProvider } from './hoverProvider';
import { CodeChangeDetector } from './codeDetector';

let detector: CodeChangeDetector | undefined;

export function activate(context: vscode.ExtensionContext) {
    const client = new AutoDocClient();
    const hoverProvider = new AutoDocHoverProvider();
    detector = new CodeChangeDetector(client, hoverProvider);

    const languages = [
        { language: 'python' },
        { language: 'typescript' },
        { language: 'javascript' },
    ];

    const hoverDisposable = vscode.languages.registerHoverProvider(
        languages,
        hoverProvider,
    );

    const generateCommand = vscode.commands.registerCommand(
        'autoDocAgent.generateNow',
        () => detector?.generateForCurrentFile(),
    );

    context.subscriptions.push(hoverDisposable, generateCommand);
    detector.start(context);

    vscode.window.showInformationMessage('Auto-Doc Agent is active.');
}

export function deactivate() {
    detector?.stop();
}
