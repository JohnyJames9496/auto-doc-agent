import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export class AutoDocClient {
    private http: AxiosInstance;

    constructor() {
        const config = vscode.workspace.getConfiguration('autoDocAgent');
        const apiUrl = config.get<string>('apiUrl', 'https://auto-doc-agent.onrender.com');
        const token = config.get<string>('jwtToken', '');

        console.log('Auto-Doc Agent: API URL is', apiUrl);
        console.log('Auto-Doc Agent: Token exists:', token.length > 0);

        this.http = axios.create({
            baseURL: apiUrl,
            timeout: 15000,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });
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
            const response = await this.http.post('/api/v1/documentation', payload);
            console.log('Auto-Doc Agent: response status', response.status);
            console.log('Auto-Doc Agent: response data', response.data);

            // If cached or already complete, return documentation directly
            if (response.data.status === 'complete' && response.data.documentation) {
                return { taskId: null, documentation: response.data.documentation };
            }

            return { taskId: response.data.task_id ?? null, documentation: null };
        } catch (err: any) {
            console.error('Auto-Doc Agent: request failed', err?.message || err);
            return { taskId: null, documentation: null };
        }
    }

    async pollTaskResult(taskId: string): Promise<{ status: string; documentation?: string } | null> {
        try {
            const response = await this.http.get(`/api/v1/documentation/task/${taskId}`);
            console.log('Auto-Doc Agent: task result', response.data);
            return response.data;
        } catch (err: any) {
            console.error('Auto-Doc Agent: poll failed', err?.message || err);
            return null;
        }
    }
}