import * as vscode from 'vscode';
import { ServerManager } from './serverManager';
import { SidebarProvider } from './sidebarProvider';

let serverManager: ServerManager;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    serverManager = new ServerManager();

    const sidebarProvider = new SidebarProvider(context.extensionUri, serverManager);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(SidebarProvider.viewType, sidebarProvider)
    );

    // Initialize Status Bar Item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(circle-slash) GitHydra: Off';
    statusBarItem.command = 'githydra.openDashboard';
    statusBarItem.tooltip = 'GitHydra server is not running';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register Commands
    context.subscriptions.push(vscode.commands.registerCommand('githydra.startServer', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('Please open a workspace folder first.');
            return;
        }

        const workspacePath = workspaceFolders[0].uri.fsPath;
        const success = await serverManager.start(workspacePath);

        if (success) {
            vscode.window.showInformationMessage(`GitHydra server started on ${serverManager.getUrl()}`);
            updateStatusBar(true);
            sidebarProvider.updateState();
        } else {
            vscode.window.showErrorMessage('Failed to start GitHydra server. Check the Output channel for details.');
        }
    }));

    context.subscriptions.push(vscode.commands.registerCommand('githydra.stopServer', () => {
        serverManager.stop();
        updateStatusBar(false);
        sidebarProvider.updateState();
        vscode.window.showInformationMessage('GitHydra server stopped.');
    }));

    context.subscriptions.push(vscode.commands.registerCommand('githydra.openDashboard', () => {
        if (serverManager.isRunning()) {
            vscode.env.openExternal(vscode.Uri.parse(serverManager.getUrl()));
        } else {
            vscode.window.showInformationMessage('GitHydra server is not running. Start it first.');
        }
    }));
}

function updateStatusBar(running: boolean) {
    if (running) {
        statusBarItem.text = `$(check) GitHydra: ${serverManager.getPort()}`;
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.remoteBackground');
        statusBarItem.tooltip = `GitHydra running at ${serverManager.getUrl()}`;
    } else {
        statusBarItem.text = '$(circle-slash) GitHydra: Off';
        statusBarItem.backgroundColor = undefined;
        statusBarItem.tooltip = 'GitHydra server is not running';
    }
}

export function deactivate() {
    if (serverManager) {
        serverManager.stop();
    }
}
