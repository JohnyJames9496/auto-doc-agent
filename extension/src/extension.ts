import * as vscode from 'vscode';
import { AutoDocClient } from './apiClient';
import { AutoDocHoverProvider } from './hoverProvider';
import { CodeChangeDetector } from './codeDetector';

// Bug #4 fix — module level for cleanup
let detector: CodeChangeDetector | undefined;
let client: AutoDocClient | undefined;

export function activate(context: vscode.ExtensionContext) {
    // Bug #3 fix — error handling
    try {
        // Bug #1 fix — check API key on activation
        const config = vscode.workspace.getConfiguration('autoDocAgent');
        const apiKey = config.get<string>('apiKey', '');

        if (!apiKey) {
            vscode.window.showWarningMessage(
                'Auto-Doc Agent: No API key configured. Get your key at auto-doc-agent.onrender.com',
                'Open Settings'
            ).then(selection => {
                if (selection === 'Open Settings') {
                    vscode.commands.executeCommand(
                        'workbench.action.openSettings',
                        'autoDocAgent.apiKey'
                    );
                }
            });
        }

        client = new AutoDocClient();
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

        // Bug #5 fix — listen for config changes
        const configListener = vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('autoDocAgent')) {
                client = new AutoDocClient();
                detector = new CodeChangeDetector(client, hoverProvider);
                detector.start(context);
                vscode.window.showInformationMessage(
                    'Auto-Doc Agent: Settings updated and applied.'
                );
            }
        });

        // File deletion cleanup (from hoverProvider fixes)
        const deleteDisposable = vscode.workspace.onDidDeleteFiles((event) => {
            event.files.forEach(file => {
                hoverProvider.clearFile(file.fsPath);
            });
        });

        context.subscriptions.push(
            hoverDisposable,
            generateCommand,
            configListener,
            deleteDisposable,
        );

        detector.start(context);

        // Bug #2 fix — show welcome only once
        const hasShownWelcome = context.globalState.get<boolean>('hasShownWelcome');
        if (!hasShownWelcome) {
            vscode.window.showInformationMessage(
                'Auto-Doc Agent is active. Start writing code to generate docs!'
            );
            context.globalState.update('hasShownWelcome', true);
        }

    } catch (error) {
        vscode.window.showErrorMessage(
            `Auto-Doc Agent failed to activate: ${error}`
        );
        console.error('Auto-Doc Agent activation error:', error);
    }
}

export function deactivate() {
    detector?.stop();
    // Bug #4 fix — cleanup client
    client = undefined;
}