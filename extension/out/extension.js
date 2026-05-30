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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const apiClient_1 = require("./apiClient");
const hoverProvider_1 = require("./hoverProvider");
const codeDetector_1 = require("./codeDetector");
let detector;
function activate(context) {
    const client = new apiClient_1.AutoDocClient();
    const hoverProvider = new hoverProvider_1.AutoDocHoverProvider();
    detector = new codeDetector_1.CodeChangeDetector(client, hoverProvider);
    const languages = [
        { language: 'python' },
        { language: 'typescript' },
        { language: 'javascript' },
    ];
    const hoverDisposable = vscode.languages.registerHoverProvider(languages, hoverProvider);
    const generateCommand = vscode.commands.registerCommand('autoDocAgent.generateNow', () => detector?.generateForCurrentFile());
    context.subscriptions.push(hoverDisposable, generateCommand);
    detector.start(context);
    vscode.window.showInformationMessage('Auto-Doc Agent is active.');
}
function deactivate() {
    detector?.stop();
}
//# sourceMappingURL=extension.js.map