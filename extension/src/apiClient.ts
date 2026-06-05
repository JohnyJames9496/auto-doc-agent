import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export class AutoDocClient {
    private http: AxiosInstance;

    constructor() {
        const config = vscode.workspace.getConfiguration('autoDocAgent');
        const apiUrl = config.get<string>('apiUrl', 'https://auto-doc-agent.onrender.com');
        const apiKey = config.get<string>('apiKey', '');

        // Bug #6 fix — warn if no API key
        if (!apiKey) {
            vscode.window.showWarningMessage(
                'Auto-Doc Agent: No API key set. Please add your key in settings.',
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

        this.http = axios.create({
            baseURL: apiUrl,
            timeout: 30000,
        });
    }

    // Bug #1 fix — read key fresh on every request
    private getHeaders() {
        const config = vscode.workspace.getConfiguration('autoDocAgent');
        const apiKey = config.get<string>('apiKey', '');
        return {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
        };
    }

    async requestDocumentation(payload: {
        file_path: string;
        function_name: string;
        code_snippet: string;
        language: string;
        project_id: string;
    }): Promise<{ taskId: string | null; documentation: string | null }> {
        try {
            console.log('Auto-Doc Agent: sending request for', payload.function_name);
            const response = await this.http.post(
                '/api/v1/documentation',
                payload,
                { headers: this.getHeaders() }
            );
            console.log('Auto-Doc Agent: response status', response.status);
            // Bug #3 fix — don't log full response
            console.log('Auto-Doc Agent: status', response.data.status);
            console.log('Auto-Doc Agent: has docs', !!response.data.documentation);

            if (response.data.status === 'complete' && response.data.documentation) {
                return { taskId: null, documentation: response.data.documentation };
            }
            return { taskId: response.data.task_id ?? null, documentation: null };

        } catch (err: any) {
            // Bug #4 fix — specific error messages
            const status = err?.response?.status;
            if (status === 401) {
                vscode.window.showErrorMessage(
                    'Auto-Doc Agent: Invalid API key. Check your settings.',
                    'Open Settings'
                ).then(s => {
                    if (s === 'Open Settings') {
                        vscode.commands.executeCommand('workbench.action.openSettings', 'autoDocAgent.apiKey');
                    }
                });
            } else if (status === 429) {
                vscode.window.showWarningMessage('Auto-Doc Agent: Rate limit reached. Try again in a moment.');
            } else if (!status) {
                vscode.window.showWarningMessage('Auto-Doc Agent: Cannot reach server. Check your internet connection.');
            } else {
                vscode.window.showErrorMessage(`Auto-Doc Agent: Request failed (${status}). Try again.`);
            }
            console.error('Auto-Doc Agent: request failed', err?.message || err);
            return { taskId: null, documentation: null };
        }
    }

    async pollTaskResult(taskId: string): Promise<{ status: string; documentation?: string } | null> {
        try {
            const response = await this.http.get(
                `/api/v1/documentation/task/${taskId}`,
                { headers: this.getHeaders() }
            );
            console.log('Auto-Doc Agent: task status', response.data.status);
            return response.data;
        } catch (err: any) {
            // Bug #5 fix — return pending-like object so polling continues
            console.error('Auto-Doc Agent: poll failed', err?.message || err);
            return { status: 'pending' };
        }
    }
}