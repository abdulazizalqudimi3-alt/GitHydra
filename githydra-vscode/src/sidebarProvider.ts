import * as vscode from 'vscode';
import { ServerManager } from './serverManager';
import axios from 'axios';

export class SidebarProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'githydra.sidebar';
    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _serverManager: ServerManager
    ) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'startServer':
                    vscode.commands.executeCommand('githydra.startServer');
                    break;
                case 'stopServer':
                    vscode.commands.executeCommand('githydra.stopServer');
                    break;
                case 'openDashboard':
                    vscode.commands.executeCommand('githydra.openDashboard');
                    break;
                case 'refresh':
                    this.updateState();
                    break;
                case 'gitOp':
                    this.performGitOp(data.op, data.params);
                    break;
            }
        });

        // Periodically update state
        setInterval(() => this.updateState(), 5000);
    }

    public async updateState() {
        if (!this._view) return;

        const isRunning = this._serverManager.isRunning();
        let gitStatus = null;

        if (isRunning) {
            try {
                const response = await axios.get(`${this._serverManager.getUrl()}/api/git/status`);
                if (response.data.success) {
                    gitStatus = response.data.data;
                }
            } catch (error) {
                // Ignore errors during polling
            }
        }

        this._view.webview.postMessage({
            type: 'updateState',
            isRunning,
            url: this._serverManager.getUrl(),
            gitStatus
        });
    }

    private async performGitOp(op: string, params: any) {
        if (!this._serverManager.isRunning()) {
            vscode.window.showErrorMessage('GitHydra server is not running.');
            return;
        }

        try {
            let response;
            const url = this._serverManager.getUrl();

            switch(op) {
                case 'stage':
                    response = await axios.post(`${url}/api/git/stage/add`, { files: params.files });
                    break;
                case 'unstage':
                    response = await axios.post(`${url}/api/git/stage/reset`, { files: params.files });
                    break;
                case 'commit':
                    response = await axios.post(`${url}/api/git/commit`, { message: params.message });
                    break;
            }

            if (response?.data.success) {
                vscode.window.showInformationMessage(response.data.message || 'Operation successful');
                this.updateState();
            } else {
                vscode.window.showErrorMessage(response?.data.error || 'Operation failed');
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`API Error: ${error.message}`);
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const styleMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'sidebar.css'));
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'sidebar.js'));

        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${styleMainUri}" rel="stylesheet">
                <title>GitHydra</title>
            </head>
            <body>
                <div id="app">
                    <div class="header">
                        <h2>GitHydra</h2>
                        <div id="server-status" class="status-badge stopped">Stopped</div>
                    </div>

                    <div id="server-controls" class="section">
                        <button id="btn-start" class="btn-primary">Start Server</button>
                        <button id="btn-stop" class="btn-secondary hidden">Stop Server</button>
                        <a id="link-dashboard" class="hidden" href="#">Open Web Dashboard</a>
                    </div>

                    <div id="git-info" class="section hidden">
                        <h3>Branch: <span id="current-branch">-</span></h3>

                        <div class="tabs">
                            <div class="tab-header">
                                <div class="tab-item active" data-tab="staged">Staged</div>
                                <div class="tab-item" data-tab="unstaged">Unstaged</div>
                            </div>
                            <div id="staged-list" class="tab-content"></div>
                            <div id="unstaged-list" class="tab-content hidden"></div>
                        </div>

                        <div class="commit-area">
                            <textarea id="commit-msg" placeholder="Commit message..."></textarea>
                            <button id="btn-commit" class="btn-primary">Commit</button>
                        </div>
                    </div>
                </div>
                <script src="${scriptUri}"></script>
            </body>
            </html>`;
    }
}
