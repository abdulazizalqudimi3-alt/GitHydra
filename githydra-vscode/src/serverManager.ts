import * as child_process from 'child_process';
import * as vscode from 'vscode';
import * as os from 'os';

export class ServerManager {
    private serverProcess: child_process.ChildProcess | null = null;
    private port: number = 5000;
    private outputChannel: vscode.OutputChannel;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('GitHydra Server');
    }

    private getPythonCommand(): string {
        // Simple detection, in a real extension we'd use the Python extension API
        return os.platform() === 'win32' ? 'python' : 'python3';
    }

    public async start(workspacePath: string, port: number = 5000): Promise<boolean> {
        if (this.serverProcess) {
            this.outputChannel.appendLine('Server is already running.');
            return true;
        }

        this.port = port;
        const pythonCmd = this.getPythonCommand();
        this.outputChannel.appendLine(`Starting GitHydra server using ${pythonCmd} for ${workspacePath} on port ${this.port}...`);

        return new Promise((resolve) => {
            const args = ['-m', 'githydra', 'web', workspacePath, '--port', this.port.toString(), '--no-browser'];

            this.serverProcess = child_process.spawn(pythonCmd, args, {
                cwd: workspacePath,
                env: { ...process.env, PYTHONUNBUFFERED: '1' }
            });

            this.serverProcess.stdout?.on('data', (data) => {
                const output = data.toString();
                this.outputChannel.append(output);
                if (output.includes('Uvicorn running on')) {
                    resolve(true);
                }
            });

            this.serverProcess.stderr?.on('data', (data) => {
                const output = data.toString();
                this.outputChannel.append(`ERROR: ${output}`);
            });

            this.serverProcess.on('close', (code) => {
                this.outputChannel.appendLine(`Server process exited with code ${code}`);
                this.serverProcess = null;
                resolve(false);
            });

            this.serverProcess.on('error', (err) => {
                this.outputChannel.appendLine(`Failed to start server: ${err.message}`);
                this.serverProcess = null;
                resolve(false);
            });

            // Fallback resolve after timeout
            setTimeout(() => {
                if (this.serverProcess) {
                    // Assume it might have started if no error yet?
                    // Better to keep it pending or resolve false.
                    // If it hasn't resolved true by now, it might be stuck.
                }
                resolve(false);
            }, 20000);
        });
    }

    public stop() {
        if (this.serverProcess) {
            this.outputChannel.appendLine('Stopping GitHydra server...');
            // On Windows we might need taskkill to kill the whole process tree
            if (os.platform() === 'win32') {
                child_process.exec(`taskkill /pid ${this.serverProcess.pid} /T /F`);
            } else {
                this.serverProcess.kill();
            }
            this.serverProcess = null;
        }
    }

    public isRunning(): boolean {
        return this.serverProcess !== null;
    }

    public getPort(): number {
        return this.port;
    }

    public getUrl(): string {
        return `http://localhost:${this.port}`;
    }
}
