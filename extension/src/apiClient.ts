import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export class AutoDocClient {
    private http: AxiosInstance;

    constructor() {
        const config = vscode.workspace.getConfiguration('autoDocAgent');
        this.http = axios.create({
            baseURL: config.get<string>('apiUrl', 'http://localhost:8000'),
            timeout: 10000,
            headers: {
                'Authorization': `Bearer ${config.get<string>('jwtToken', '')}`,
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
    }): Promise<string | null> {
        try {
            const response = await this.http.post('/api/v1/documentation', payload);
            return response.data.task_id ?? null;
        } catch {
            return null;
        }
    }

    async pollTaskResult(taskId: string): Promise<{ status: string; documentation?: string } | null> {
        try {
            const response = await this.http.get(`/api/v1/documentation/task/${taskId}`);
            return response.data;
        } catch {
            return null;
        }
    }
}
